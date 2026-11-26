from django.urls import path
from .views import (
    CustomerPaymentListAPIView,
    ProviderPaymentListAPIView,
    CustomerPaymentCreateAPIView,
    PaymentInitiationAPIView,
    PaymentWebhookAPIView,
    CustomerDisputeCreateAPIView,
    ProviderDisputeListAPIView,
    ProviderDisputeResponseAPIView,
     AdminDisputeResolutionAPIView,
)

urlpatterns = [
    path("my-payments/", CustomerPaymentListAPIView.as_view(), name="customer-payments"),
    path("provider-payments/", ProviderPaymentListAPIView.as_view(), name="provider-payments"),
    path("create/", CustomerPaymentCreateAPIView.as_view(), name="create-payment"),
    path("initiate/", PaymentInitiationAPIView.as_view(), name="payment-initiate"),
    path("webhook/", PaymentWebhookAPIView.as_view(), name="payment-webhook"),
    path("disputes/create/", CustomerDisputeCreateAPIView.as_view(), name="create-dispute"),
    path("provider-disputes/", ProviderDisputeListAPIView.as_view(), name="provider-disputes"),
    path("provider-disputes/<int:pk>/respond/", ProviderDisputeResponseAPIView.as_view(), name="provider-dispute-respond"),
    path( "admin-disputes/<int:pk>/resolve/", AdminDisputeResolutionAPIView.as_view(), name="admin-dispute-resolve"),
]