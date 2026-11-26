
from django.conf import settings
from django.db import models


class Provider(models.Model):

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider"
    )

    tagline = models.CharField(max_length=150)
    bio = models.TextField()
    suburb = models.CharField(max_length=100)
    years_experience = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    skills = models.TextField(
        help_text="Enter the provider's skills, separated by commas."
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.verification_status}"
