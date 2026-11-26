
from django.urls import path

from .views import (
    ServiceListAPIView,
    ProviderServiceListCreateAPIView,
    ProviderServiceDetailAPIView,
)

urlpatterns = [
    # Public service listing
    path("", ServiceListAPIView.as_view(), name="service-list"),

    # Provider service management
    path(
        "my-services/",
        ProviderServiceListCreateAPIView.as_view(),
        name="provider-service-list-create",
    ),

    # Update, view or delete an individual service
    path(
        "my-services/<int:pk>/",
        ProviderServiceDetailAPIView.as_view(),
        name="provider-service-detail",
    ),
]
