from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import Profile, ProfileSample

User = get_user_model()


class BootstrapFormMixin:
    """Adds Bootstrap 5 CSS classes to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(widget, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "profile_image",
            "department",
            "year_of_study",
            "location",
            "bio",
            "skills_have",
            "skills_want",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}


class SampleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ProfileSample
        fields = ["title", "file"]
