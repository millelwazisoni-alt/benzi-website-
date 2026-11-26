
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Service
from .serializers import ServiceSerializer


class ServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Service.objects.filter(
            is_active=True,
            provider__verification_status="APPROVED"
        )


class ProviderServiceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Service.objects.none()

        return Service.objects.filter(
            provider=self.request.user.provider
        )

    def perform_create(self, serializer):
        if not hasattr(self.request.user, "provider"):
            raise PermissionDenied(
                "You must have a provider profile to create services."
            )

        if self.request.user.provider.verification_status != "APPROVED":
            raise PermissionDenied(
                "Your provider account must be approved before creating services."
            )

        serializer.save(provider=self.request.user.provider)


class ProviderServiceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "provider"):
            return Service.objects.none()

        return Service.objects.filter(
            provider=self.request.user.provider
        )
