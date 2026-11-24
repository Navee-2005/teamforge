from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from .forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
    SampleForm,
    StyledPasswordChangeForm,
)
from .mixins import DeleteMessageMixin
from .models import Profile, ProfileSample


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:profile_edit")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("collab:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # start the session straight away
        messages.success(
            self.request,
            "Welcome to TeamForge! Complete your profile so teams can find you.",
        )
        return response


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_me"] = self.object.user_id == self.request.user.id
        context["ideas"] = self.object.user.ideas.all()[:6]
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"
    success_message = "Profile updated."

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class SampleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = SampleForm
    template_name = "accounts/sample_form.html"
    success_message = "Sample uploaded."

    def form_valid(self, form):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.user.profile.get_absolute_url()


class SampleDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    template_name = "confirm_delete.html"
    success_message = "Sample deleted."

    def get_queryset(self):
        return ProfileSample.objects.filter(profile__user=self.request.user)

    def get_success_url(self):
        return self.request.user.profile.get_absolute_url()


class DeleteAccountView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/delete_account.html"

    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account and profile were deleted.")
        return redirect("collab:home")


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class UserPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
