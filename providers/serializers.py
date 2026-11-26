

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from users.models import UserProfile
from .models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Provider
        fields = [
            "id",
            "provider_name",
            "tagline",
            "bio",
            "suburb",
            "years_experience",
            "hourly_rate",
            "skills",
            "verification_status",
            "created_at",
        ]


class ProviderRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = Provider
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "tagline",
            "bio",
            "suburb",
            "years_experience",
            "hourly_rate",
            "skills",
        ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.PROVIDER,
        )

        provider = Provider.objects.create(
            user=user,
            **validated_data,
        )

        return provider
