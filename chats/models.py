from django.db import models
from django.conf import settings


class Trip(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("planning", "Planning"),
        ("ready", "Ready"),
        ("archived", "Archived"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips",
    )

    title = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    travelers_count = models.PositiveIntegerField(default=1)
    budget = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.destination})"


class TripMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"
