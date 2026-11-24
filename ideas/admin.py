from django.contrib import admin

from .models import Milestone, ProjectIdea


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(ProjectIdea)
class ProjectIdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "level", "team_size", "status", "created_at")
    list_filter = ("category", "level", "status")
    search_fields = ("title", "required_skills", "owner__username")
    inlines = [MilestoneInline]
