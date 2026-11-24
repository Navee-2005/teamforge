from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from accounts.models import split_skills


class ProjectIdea(models.Model):
    CATEGORY_CHOICES = [
        ("web", "Web Development"),
        ("mobile", "Mobile App"),
        ("ai", "AI / Machine Learning"),
        ("data", "Data Science"),
        ("iot", "IoT / Hardware"),
        ("game", "Game Development"),
        ("other", "Other"),
    ]
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="web")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    required_skills = models.CharField(
        max_length=300,
        help_text="Comma separated skills you need, e.g. React, Django, UI/UX",
    )
    team_size = models.PositiveSmallIntegerField(
        default=4,
        validators=[MinValueValidator(2), MaxValueValidator(10)],
        help_text="Total team size including you (2-10).",
    )
    hackathon_name = models.CharField(
        "Hackathon / event", max_length=150, blank=True
    )
    thumbnail = models.ImageField(upload_to="ideas/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ideas:detail", kwargs={"pk": self.pk})

    # ---- skills --------------------------------------------------------
    def required_skill_list(self):
        return split_skills(self.required_skills)

    # ---- team ----------------------------------------------------------
    def accepted_count(self):
        return self.join_requests.filter(status="accepted").count()

    def spots_left(self):
        return max(self.team_size - 1 - self.accepted_count(), 0)

    def is_full(self):
        return self.spots_left() == 0

    def team_members(self):
        return get_user_model().objects.filter(
            join_requests__idea=self, join_requests__status="accepted"
        )

    # ---- progress tracker ----------------------------------------------
    def overall_progress(self):
        values = list(self.milestones.values_list("progress", flat=True))
        return round(sum(values) / len(values)) if values else 0


class Milestone(models.Model):
    """Team progress tracker entry for a project idea."""

    idea = models.ForeignKey(
        ProjectIdea, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=150)
    notes = models.TextField(blank=True)
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 to 100",
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.title} ({self.progress}%)"

    def save(self, *args, **kwargs):
        if self.is_completed:
            self.progress = 100
        super().save(*args, **kwargs)
