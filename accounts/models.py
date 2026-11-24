from django.conf import settings
from django.db import models
from django.urls import reverse


def split_skills(text):
    """'Python, React ,  ' -> ['Python', 'React']"""
    return [s.strip() for s in (text or "").split(",") if s.strip()]


class Profile(models.Model):
    YEAR_CHOICES = [
        (1, "1st year"),
        (2, "2nd year"),
        (3, "3rd year"),
        (4, "4th year"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.PositiveSmallIntegerField(
        choices=YEAR_CHOICES, blank=True, null=True
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills_have = models.CharField(
        "Skills I have",
        max_length=300,
        blank=True,
        help_text="Comma separated, e.g. Python, React, UI/UX",
    )
    skills_want = models.CharField(
        "Skills I want to learn",
        max_length=300,
        blank=True,
        help_text="Comma separated, e.g. Django, Docker",
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"pk": self.pk})

    def have_list(self):
        return split_skills(self.skills_have)

    def want_list(self):
        return split_skills(self.skills_want)


class ProfileSample(models.Model):
    """Certificates or project samples uploaded to a profile."""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="samples"
    )
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to="samples/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title
