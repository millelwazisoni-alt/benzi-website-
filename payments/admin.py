

from django.contrib import admin
from .models import Payment, Dispute


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "customer",
        "provider",
        "amount",
        "benzi_commission",
        "provider_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "payment_reference",
        "customer__username",
        "provider__user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment",
        "raised_by",
        "reason",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "raised_by__username",
        "reason",
        "payment__payment_reference",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
