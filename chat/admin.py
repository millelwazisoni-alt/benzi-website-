from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "provider",
        "booking",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "customer__username",
        "provider__user__username",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "sender",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = (
        "sender__username",
        "content",
    )
    readonly_fields = ("created_at",)