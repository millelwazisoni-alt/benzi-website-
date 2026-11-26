from django.db import models


class Service(models.Model):
    class Category(models.TextChoices):
        IT = "IT", "IT Support"
        CLEANING = "CLEANING", "Cleaning"
        TUTORING = "TUTORING", "Tutoring"
        NANNY = "NANNY", "Nanny Services"

    provider = models.ForeignKey(
        "providers.Provider",
        on_delete=models.CASCADE,
        related_name="services",
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    suburb = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.provider}"