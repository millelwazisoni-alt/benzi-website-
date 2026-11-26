from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "provider",
        "category",
        "price",
        "suburb",
        "is_active",
    )
    list_filter = ("category", "is_active", "suburb")
    search_fields = ("title", "description", "suburb")
