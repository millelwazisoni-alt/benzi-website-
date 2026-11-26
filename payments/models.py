from django.db import models
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        HELD = "HELD", "Held"
        DISPUTE_WINDOW = "DISPUTE_WINDOW", "Dispute Window"
        DISPUTED = "DISPUTED", "Disputed"
        RELEASE_PENDING = "RELEASE_PENDING", "Release Pending"
        RELEASED = "RELEASED", "Released"
        REFUNDED = "REFUNDED", "Refunded"

    booking = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.PROTECT,
        related_name="payment",
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments_made",
    )

    provider = models.ForeignKey(
        "providers.Provider",
        on_delete=models.PROTECT,
        related_name="payments_received",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    benzi_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    provider_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )

    payment_provider = models.CharField(
    max_length=50,
    blank=True,
    null=True,
)

    dispute_window_started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    payout_eligible_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.pk} - {self.status}"

    def calculate_commission(self):
        self.benzi_commission = (
            self.amount * Decimal("0.20")
        ).quantize(Decimal("0.01"))

        self.provider_amount = self.amount - self.benzi_commission
    def save(self, *args, **kwargs):
        self.calculate_commission()
        super().save(*args, **kwargs)


class Dispute(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"

    class ResolutionDecision(models.TextChoices):
        REFUND = "REFUND", "Refund Customer"
        RELEASE_PAYOUT = "RELEASE_PAYOUT", "Release Provider Payout"

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="dispute",
    )

    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="disputes_raised",
    )

    reason = models.CharField(max_length=150)
    description = models.TextField()

    provider_response = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    resolution_decision = models.CharField(
        max_length=20,
        choices=ResolutionDecision.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Dispute #{self.pk} - Payment #{self.payment_id}"


   

