from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "service",
        "scheduled_for",
        "agreed_price",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "customer__username",
        "service__title",
        "suburb",
    )

    readonly_fields = ("created_at", "updated_at")