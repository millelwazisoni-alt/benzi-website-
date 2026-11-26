

from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(
        source="service.title",
        read_only=True
    )
    provider_name = serializers.CharField(
        source="service.provider.user.get_full_name",
        read_only=True
    )
    customer_name = serializers.CharField(
        source="customer.get_full_name",
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer",
            "customer_name",
            "service",
            "service_title",
            "provider_name",
            "scheduled_for",
            "suburb",
            "address_details",
            "notes",
            "agreed_price",
            "status",
            "provider_completed",
            "customer_completed",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "customer_name",
            "service_title",
            "provider_name",
            "agreed_price",
            "status",
            "provider_completed",
            "customer_completed",
            "created_at",
            "updated_at",
        ]
