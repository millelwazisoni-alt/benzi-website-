from rest_framework import generics, permissions

from .models import Provider
from .serializers import ProviderSerializer, ProviderRegistrationSerializer


class ProviderListAPIView(generics.ListAPIView):
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Provider.objects.filter(
            verification_status=Provider.VerificationStatus.APPROVED
        )

class ProviderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProviderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Provider.objects.filter(
            verification_status=Provider.VerificationStatus.APPROVED
        )


class ProviderRegistrationAPIView(generics.CreateAPIView):
    serializer_class = ProviderRegistrationSerializer
    permission_classes = [permissions.AllowAny]





from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.models import Booking
from payments.models import Payment


class ProviderDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "provider"):
            return Response(
                {"error": "You do not have a provider account."},
                status=403
            )

        provider = request.user.provider

        bookings = Booking.objects.filter(
            service__provider=provider
        )

        payments = Payment.objects.filter(provider=provider)
        earnings_payments = payments.filter(
            status__in=[
                "HELD",
                "DISPUTE_WINDOW",
                "RELEASE_PENDING",
                "RELEASED",
            ]
        )

        pending_payouts = payments.filter(
            status__in=[
                "HELD",
                "DISPUTE_WINDOW",
                "RELEASE_PENDING",
            ]
        )

        completed_payouts = payments.filter(
            status="RELEASED"
        )

        earnings_statuses = [
            "DISPUTE_WINDOW",
            "RELEASE_PENDING",
            "RELEASED",
        ]

        data = {
            "total_bookings": bookings.count(),
            "pending_bookings": bookings.filter(status="PENDING").count(),
            "accepted_bookings": bookings.filter(status="ACCEPTED").count(),
            "completed_bookings": bookings.filter(status="COMPLETED").count(),
            "cancelled_bookings": bookings.filter(status="CANCELLED").count(),
            "total_payments": payments.count(),

            "total_earnings": sum(
    payment.provider_amount for payment in earnings_payments
),

"pending_payout": sum(
    payment.provider_amount for payment in pending_payouts
),

"paid_out": sum(
    payment.provider_amount for payment in completed_payouts
),
            

           

            "recent_bookings": [],
        }

        recent = bookings.order_by("-created_at")[:5]

        data["recent_bookings"] = [
            {
                "id": booking.id,
                "service": booking.service.title,
                "customer": booking.customer.get_full_name(),
                "status": booking.status,
                "price": booking.agreed_price,
                "created_at": booking.created_at,
            }
            for booking in recent
        ]

        return Response(data)