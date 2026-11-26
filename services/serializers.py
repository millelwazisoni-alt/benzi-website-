from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(
        source="provider.user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Service
        fields = [
            "id",
            "provider",
            "provider_name",
            "title",
            "description",
            "category",
            "price",
            "suburb",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "provider",
            "provider_name",
            "created_at",
        ]