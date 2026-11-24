from django import forms

from accounts.forms import BootstrapFormMixin

from .models import JoinRequest


class JoinRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Hi! I can help with..."}
            )
        }
