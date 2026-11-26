from rest_framework import serializers
from .models import Payment, Dispute


class PaymentSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(
        source="booking.service.title",
        read_only=True,
    )

    customer_name = serializers.CharField(
        source="customer.get_full_name",
        read_only=True,
    )

    provider_name = serializers.CharField(
        source="provider.user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "service_title",
            "customer",
            "customer_name",
            "provider",
            "provider_name",
            "amount",
            "benzi_commission",
            "provider_amount",
            "status",
            "payment_reference",
            "payment_provider",
            "dispute_window_started_at",
            "payout_eligible_at",
            "created_at",
            "updated_at",
            
        ]

        read_only_fields = fields

class PaymentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ["booking"]

    def validate_booking(self, booking):
        user = self.context["request"].user

        if booking.customer != user:
            raise serializers.ValidationError(
                "You can only pay for your own bookings."
            )

        if booking.status != "ACCEPTED":
            raise serializers.ValidationError(
                "The booking must be accepted before payment."
            )

        if hasattr(booking, "payment"):
            raise serializers.ValidationError(
                "A payment record already exists for this booking."
            )

        return booking

    def create(self, validated_data):
        booking = validated_data["booking"]

        return Payment.objects.create(
            booking=booking,
            customer=booking.customer,
            provider=booking.service.provider,
            amount=booking.agreed_price,
        )


from .models import Dispute


class DisputeSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.CharField(
        source="raised_by.username",
        read_only=True,
    )

    payment_id = serializers.IntegerField(
        source="payment.id",
        read_only=True,
    )

    class Meta:
        model = Dispute
        fields = [
            "id",
            "payment_id",
            "raised_by",
            "raised_by_name",
            "reason",
            "description",
            "provider_response",
            "status",
            "resolution_notes",
            "created_at",
            "updated_at",
            "resolved_at",
        ]

        read_only_fields = [
            "id",
            "payment_id",
            "raised_by",
            "raised_by_name",
            "provider_response",
            "status",
            "resolution_notes",
            "created_at",
            "updated_at",
            "resolved_at",
        ]


class ProviderDisputeResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dispute
        fields = [
            "id",
            "provider_response",
            "status",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "updated_at",
        ]

    def validate_provider_response(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "A provider response is required."
            )

        return value

class AdminDisputeResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = [
            "id",
            "status",
            "resolution_decision",
            "resolution_notes",
            "resolved_at",
        ]
        read_only_fields = [
            "id",
            "resolved_at",
        ]

    def validate_status(self, value):
        if value != Dispute.Status.RESOLVED:
            raise serializers.ValidationError(
                "A dispute must be marked as resolved."
            )
        return value

    def validate_resolution_decision(self, value):
        if value not in [
            Dispute.ResolutionDecision.REFUND,
            Dispute.ResolutionDecision.RELEASE_PAYOUT,
        ]:
            raise serializers.ValidationError(
                "Choose REFUND or RELEASE_PAYOUT."
            )
        return value

    def validate_resolution_notes(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Resolution notes are required."
            )
        return value