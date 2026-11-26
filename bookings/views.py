from datetime import timedelta

from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer
from payments.models import Payment


class CustomerBookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user
        ).select_related(
            "service",
            "service__provider",
            "service__provider__user",
        )

    def perform_create(self, serializer):
        service_id = self.request.data.get("service")

        from services.models import Service

        try:
            service = Service.objects.get(
                id=service_id,
                is_active=True,
                provider__verification_status="APPROVED",
            )
        except (Service.DoesNotExist, ValueError, TypeError):
            raise PermissionDenied(
                "This service is unavailable for booking."
            )

        serializer.save(
            customer=self.request.user,
            service=service,
            agreed_price=service.price,
        )


class ProviderBookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Booking.objects.none()

        return Booking.objects.filter(
            service__provider=self.request.user.provider
        ).select_related(
            "customer",
            "service",
            "service__provider",
            "service__provider__user",
        )


class ProviderBookingStatusAPIView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Booking.objects.none()

        return Booking.objects.filter(
            service__provider=self.request.user.provider,
            status=Booking.Status.PENDING,
        )

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        new_status = request.data.get("status")

        if new_status not in [
            Booking.Status.ACCEPTED,
            Booking.Status.DECLINED,
        ]:
            raise PermissionDenied(
                "You can only accept or decline pending bookings."
            )

        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(booking).data)


class CustomerBookingCancelAPIView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user,
            status__in=[
                Booking.Status.PENDING,
                Booking.Status.ACCEPTED,
            ],
        )

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(booking).data)


class ProviderCompletionConfirmAPIView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Booking.objects.none()

        return Booking.objects.filter(
            service__provider=self.request.user.provider,
            status=Booking.Status.ACCEPTED,
        )

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        booking.provider_completed = True

        if booking.customer_completed:
            booking.status = Booking.Status.COMPLETED

        booking.save(
            update_fields=[
                "provider_completed",
                "status",
                "updated_at",
            ]
        )

        if booking.status == Booking.Status.COMPLETED:
            self.start_dispute_window(booking)

        return Response(self.get_serializer(booking).data)

    def start_dispute_window(self, booking):
        try:
            payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            return

        if payment.status == Payment.Status.HELD:
            now = timezone.now()

            payment.status = Payment.Status.DISPUTE_WINDOW
            payment.dispute_window_started_at = now
            payment.payout_eligible_at = now + timedelta(hours=24)

            payment.save(
                update_fields=[
                    "status",
                    "dispute_window_started_at",
                    "payout_eligible_at",
                    "updated_at",
                ]
            )


class CustomerCompletionConfirmAPIView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "options"]

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user,
            status=Booking.Status.ACCEPTED,
        )

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        booking.customer_completed = True

        if booking.provider_completed:
            booking.status = Booking.Status.COMPLETED

        booking.save(
            update_fields=[
                "customer_completed",
                "status",
                "updated_at",
            ]
        )

        if booking.status == Booking.Status.COMPLETED:
            self.start_dispute_window(booking)

        return Response(self.get_serializer(booking).data)

    def start_dispute_window(self, booking):
        try:
            payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            return

        if payment.status == Payment.Status.HELD:
            now = timezone.now()

            payment.status = Payment.Status.DISPUTE_WINDOW
            payment.dispute_window_started_at = now
            payment.payout_eligible_at = now + timedelta(hours=24)

            payment.save(
                update_fields=[
                    "status",
                    "dispute_window_started_at",
                    "payout_eligible_at",
                    "updated_at",
                ]
            )
class CustomerBookingHistoryAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.filter(
            customer=self.request.user
        ).select_related(
            "customer",
            "service",
            "service__provider",
            "service__provider__user",
        ).order_by("-created_at")

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset


class ProviderBookingHistoryAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Booking.objects.none()

        queryset = Booking.objects.filter(
            service__provider=self.request.user.provider
        ).select_related(
            "customer",
            "service",
            "service__provider",
            "service__provider__user",
        ).order_by("-created_at")

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status.upper())

        return queryset



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.models import Booking
from payments.models import Payment


class CustomerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user)

        payments = Payment.objects.filter(customer=request.user)

        data = {
            "total_bookings": bookings.count(),
            "pending_bookings": bookings.filter(status="PENDING").count(),
            "accepted_bookings": bookings.filter(status="ACCEPTED").count(),
            "completed_bookings": bookings.filter(status="COMPLETED").count(),
            "cancelled_bookings": bookings.filter(status="CANCELLED").count(),
            "total_payments": payments.count(),
            "total_spent": sum(
    payment.amount
    for payment in payments.filter(
        status__in=["HELD", "DISPUTE_WINDOW", "RELEASE_PENDING", "RELEASED"]
    )
),
            "recent_bookings": [],
        }

        recent = bookings.order_by("-created_at")[:5]

        data["recent_bookings"] = [
            {
                "id": booking.id,
                "service": booking.service.title,
                "provider": booking.service.provider.user.get_full_name(),
                "status": booking.status,
                "price": booking.agreed_price,
                "created_at": booking.created_at,
            }
            for booking in recent
        ]

        return Response(data)