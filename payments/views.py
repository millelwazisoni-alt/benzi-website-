import hmac
import hashlib

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Payment, Dispute
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    DisputeSerializer,
    ProviderDisputeResponseSerializer,
     AdminDisputeResolutionSerializer,
)



class CustomerPaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.filter(
            customer=self.request.user
        ).select_related(
            "booking",
            "booking__service",
            "customer",
            "provider",
            "provider__user",
        ).order_by("-created_at")

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset


class ProviderPaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Payment.objects.none()

        queryset = Payment.objects.filter(
            provider=self.request.user.provider
        ).select_related(
            "booking",
            "booking__service",
            "customer",
            "provider",
            "provider__user",
        ).order_by("-created_at")

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset

class CustomerPaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentInitiationAPIView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get("payment_id")

        if not payment_id:
            return Response(
                {"error": "Payment ID is required."},
                status=400,
            )

        try:
            payment = Payment.objects.get(
                id=payment_id,
                customer=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found."},
                status=404,
            )

        if payment.status != Payment.Status.PENDING:
            return Response(
                {"error": "This payment cannot be initiated."},
                status=400,
            )

        if payment.payment_provider:
            return Response(
                {"error": "A payment provider has already been selected."},
                status=400,
            )

        payment.payment_provider = "TEST"
        payment.save(update_fields=["payment_provider", "updated_at"])

        return Response({
            "message": "Payment prepared for processing.",
            "payment": self.get_serializer(payment).data,
        })

class PaymentWebhookAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        signature = request.headers.get(
            "X-Benzi-Signature", ""
        )

        expected_signature = hmac.new(
            settings.PAYMENT_WEBHOOK_SECRET.encode(),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            signature,
            expected_signature
        ):
            return Response(
                {"error": "Invalid webhook signature."},
                status=401,
            )

        payment_id = request.data.get("payment_id")
        event = request.data.get("event")

        if event != "payment.succeeded":
            return Response(
                {"error": "Unsupported payment event."},
                status=400,
            )

        try:
            payment = Payment.objects.get(id=payment_id)
        except (Payment.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Payment not found."},
                status=404,
            )

        if payment.payment_provider != "TEST":
            return Response(
                {"error": "Payment is not using the test provider."},
                status=400,
            )

        if payment.status != Payment.Status.PENDING:
            return Response(
                {"error": "Payment cannot be updated from its current status."},
                status=400,
            )

        payment.status = Payment.Status.HELD
        payment.save(update_fields=["status", "updated_at"])

        return Response({
            "message": "Simulated payment confirmation received.",
            "payment_id": payment.id,
            "status": payment.status,
        })


class CustomerDisputeCreateAPIView(generics.CreateAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        payment_id = request.data.get("payment_id")

        if not payment_id:
            return Response(
                {"error": "Payment ID is required."},
                status=400,
            )

        try:
            payment = Payment.objects.select_for_update().get(
                id=payment_id,
                customer=request.user,
            )
        except (Payment.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Payment not found."},
                status=404,
            )

        if payment.status != Payment.Status.DISPUTE_WINDOW:
            return Response(
                {"error": "This payment is not within its dispute window."},
                status=400,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dispute = serializer.save(
            payment=payment,
            raised_by=request.user,
        )

        payment.status = Payment.Status.DISPUTED
        payment.payout_eligible_at = None

        payment.save(
            update_fields=[
                "status",
                "payout_eligible_at",
                "updated_at",
            ]
        )

        return Response(
            DisputeSerializer(dispute).data,
            status=201,
        )

class ProviderDisputeListAPIView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dispute.objects.filter(
            payment__provider__user=self.request.user
        ).select_related(
            "payment",
            "raised_by",
            "payment__booking",
        ).order_by("-created_at")


class ProviderDisputeResponseAPIView(generics.UpdateAPIView):
    serializer_class = ProviderDisputeResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        return Dispute.objects.filter(
            payment__provider__user=self.request.user,
            status__in=[
                Dispute.Status.OPEN,
                Dispute.Status.UNDER_REVIEW,
            ],
        )

    def update(self, request, *args, **kwargs):
        dispute = self.get_object()

        serializer = self.get_serializer(
            dispute,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        dispute = serializer.save(
            status=Dispute.Status.UNDER_REVIEW
        )

        return Response(DisputeSerializer(dispute).data)

class AdminDisputeResolutionAPIView(generics.UpdateAPIView):
    serializer_class = AdminDisputeResolutionSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        return Dispute.objects.filter(
            status__in=[
                Dispute.Status.OPEN,
                Dispute.Status.UNDER_REVIEW,
            ]
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        dispute = self.get_object()

        dispute = Dispute.objects.select_for_update().get(
            pk=dispute.pk
        )

        serializer = self.get_serializer(
            dispute,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        dispute = serializer.save(
            resolved_at=timezone.now()
        )

        payment = Payment.objects.select_for_update().get(
            pk=dispute.payment_id
        )

        if dispute.resolution_decision == Dispute.ResolutionDecision.REFUND:
            payment.status = Payment.Status.REFUNDED

        elif dispute.resolution_decision == Dispute.ResolutionDecision.RELEASE_PAYOUT:
            payment.status = Payment.Status.RELEASE_PENDING

        payment.save(update_fields=["status", "updated_at"])

        return Response({
            "message": "Dispute resolved successfully.",
            "dispute": DisputeSerializer(dispute).data,
            "payment_status": payment.status,
        })