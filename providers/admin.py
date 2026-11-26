

from django.contrib import admin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "suburb",
        "years_experience",
        "hourly_rate",
        "verification_status",
        "created_at",
    )

    list_filter = (
        "verification_status",
        "suburb",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "suburb",
        "skills",
    )

    actions = ["approve_providers", "reject_providers"]

    @admin.action(description="Approve selected providers")
    def approve_providers(self, request, queryset):
        queryset.update(
            verification_status=Provider.VerificationStatus.APPROVED
        )

    @admin.action(description="Reject selected providers")
    def reject_providers(self, request, queryset):
        queryset.update(
            verification_status=Provider.VerificationStatus.REJECTED
        )
