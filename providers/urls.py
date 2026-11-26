from django.urls import path
from .views import (ProviderListAPIView, 
                    ProviderDashboardAPIView, 
                    ProviderDetailAPIView,
                    )

urlpatterns = [
    path("", ProviderListAPIView.as_view(), name="provider-list"),
    path("dashboard/", ProviderDashboardAPIView.as_view(), name="provider-dashboard"),
    path("<int:pk>/", ProviderDetailAPIView.as_view(), name="provider-detail"),
]