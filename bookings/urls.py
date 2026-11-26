


from django.urls import path

from .views import (
    CustomerBookingListCreateAPIView,
    ProviderBookingListAPIView,
    ProviderBookingStatusAPIView,
     CustomerBookingCancelAPIView,
     ProviderCompletionConfirmAPIView,
    CustomerCompletionConfirmAPIView,
    CustomerBookingHistoryAPIView,
    ProviderBookingHistoryAPIView,
    CustomerDashboardAPIView,
)

urlpatterns = [
    path(
        "my-bookings/",
        CustomerBookingListCreateAPIView.as_view(),
        name="customer-bookings",
    ),
    path(
        "provider-bookings/",
        ProviderBookingListAPIView.as_view(),
        name="provider-bookings",
    ),
    path(
        "provider-bookings/<int:pk>/status/",
        ProviderBookingStatusAPIView.as_view(),
        name="provider-booking-status",
    ),
    path(
    "my-bookings/<int:pk>/cancel/",
    CustomerBookingCancelAPIView.as_view(),
    name="customer-booking-cancel",
),
path(
    "provider-bookings/<int:pk>/confirm-completion/",
    ProviderCompletionConfirmAPIView.as_view(),
    name="provider-confirm-completion",
),
path(
    "my-bookings/<int:pk>/confirm-completion/",
    CustomerCompletionConfirmAPIView.as_view(),
    name="customer-confirm-completion",
),
path(
    "history/",
    CustomerBookingHistoryAPIView.as_view(),
    name="customer-booking-history",
),
path(
    "provider-history/",
    ProviderBookingHistoryAPIView.as_view(),
    name="provider-booking-history",
),
path(
    "customer-dashboard/", 
    CustomerDashboardAPIView.as_view(), 
    name="customer-dashboard"),
]
