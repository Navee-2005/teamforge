from django.contrib import admin

from .models import Profile, ProfileSample


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "year_of_study", "location")
    search_fields = ("user__username", "department", "skills_have")


@admin.register(ProfileSample)
class ProfileSampleAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "uploaded_at")
