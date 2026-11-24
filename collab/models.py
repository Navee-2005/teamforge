from django.conf import settings
from django.db import models


class JoinRequest(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
    ]
    BADGES = {
        PENDING: "warning text-dark",
        ACCEPTED: "success",
        REJECTED: "danger",
        CANCELLED: "secondary",
    }

    idea = models.ForeignKey(
        "ideas.ProjectIdea", on_delete=models.CASCADE, related_name="join_requests"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_requests"
    )
    message = models.TextField(
        help_text="Tell the owner why you want to join and what you can contribute."
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["idea", "applicant"], name="unique_join_request"
            )
        ]

    def __str__(self):
        return f"{self.applicant} -> {self.idea} ({self.status})"

    @property
    def badge_class(self):
        return self.BADGES.get(self.status, "secondary")


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"To {self.recipient}: {self.message[:40]}"
