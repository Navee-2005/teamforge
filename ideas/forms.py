from django import forms

from accounts.forms import BootstrapFormMixin

from .models import Milestone, ProjectIdea


class IdeaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectIdea
        fields = [
            "title",
            "description",
            "category",
            "level",
            "required_skills",
            "team_size",
            "hackathon_name",
            "thumbnail",
            "status",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class MilestoneForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["title", "notes", "progress", "is_completed"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
