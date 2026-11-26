from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/services/", include("services.urls")),
    path("api/providers/", include("providers.urls")),
    path("api/users/", include("users.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/payments/", include("payments.urls")),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("providers/", TemplateView.as_view(template_name="providers.html"), name="providers"),
    path("profiles/", TemplateView.as_view(template_name="profiles.html"), name="profiles"),
    path("bookings/", TemplateView.as_view(template_name="booking.html"), name="booking"),
]