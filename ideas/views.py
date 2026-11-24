from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import DeleteMessageMixin

from .forms import IdeaForm, MilestoneForm
from .models import Milestone, ProjectIdea
from .utils import match_people_for


# --------------------------------------------------------------------------
# Project ideas (marketplace)
# --------------------------------------------------------------------------
class IdeaListView(LoginRequiredMixin, ListView):
    model = ProjectIdea
    template_name = "ideas/idea_list.html"
    context_object_name = "ideas"
    paginate_by = 6

    def get_queryset(self):
        qs = ProjectIdea.objects.select_related("owner")
        params = self.request.GET
        q = params.get("q", "").strip()
        category = params.get("category", "")
        level = params.get("level", "")
        status = params.get("status", "")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(required_skills__icontains=q)
                | Q(hackathon_name__icontains=q)
            )
        if category:
            qs = qs.filter(category=category)
        if level:
            qs = qs.filter(level=level)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "q": self.request.GET.get("q", ""),
                "selected_category": self.request.GET.get("category", ""),
                "selected_level": self.request.GET.get("level", ""),
                "selected_status": self.request.GET.get("status", ""),
                "categories": ProjectIdea.CATEGORY_CHOICES,
                "levels": ProjectIdea.LEVEL_CHOICES,
                "querystring": params.urlencode(),
            }
        )
        return context


class MyIdeasView(LoginRequiredMixin, ListView):
    template_name = "ideas/my_ideas.html"
    context_object_name = "ideas"
    paginate_by = 6

    def get_queryset(self):
        return ProjectIdea.objects.filter(owner=self.request.user)


class IdeaDetailView(LoginRequiredMixin, DetailView):
    model = ProjectIdea
    template_name = "ideas/idea_detail.html"
    context_object_name = "idea"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea = self.object
        user = self.request.user
        is_owner = idea.owner_id == user.id
        my_request = idea.join_requests.filter(applicant=user).first()
        context.update(
            {
                "is_owner": is_owner,
                "my_request": my_request,
                "can_apply": (
                    not is_owner
                    and idea.status == "open"
                    and not idea.is_full()
                    and (my_request is None or my_request.status == "cancelled")
                ),
                "milestones": idea.milestones.all(),
                "team": idea.team_members().select_related("profile"),
            }
        )
        if is_owner:
            context["pending_requests"] = idea.join_requests.filter(
                status="pending"
            ).select_related("applicant", "applicant__profile")
            context["suggested_people"] = match_people_for(idea)
        return context


class IdeaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = IdeaForm
    template_name = "ideas/idea_form.html"
    success_message = "Project idea posted."

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerIdeaQuerysetMixin:
    def get_queryset(self):
        return ProjectIdea.objects.filter(owner=self.request.user)


class IdeaUpdateView(
    LoginRequiredMixin, OwnerIdeaQuerysetMixin, SuccessMessageMixin, UpdateView
):
    form_class = IdeaForm
    template_name = "ideas/idea_form.html"
    success_message = "Project idea updated."


class IdeaDeleteView(
    LoginRequiredMixin, OwnerIdeaQuerysetMixin, DeleteMessageMixin, DeleteView
):
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("ideas:mine")
    success_message = "Project idea deleted."

    def get_cancel_url(self):
        return self.object.get_absolute_url()


# --------------------------------------------------------------------------
# Milestones (team progress tracker) - only the idea owner can manage them
# --------------------------------------------------------------------------
class IdeaOwnerMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.idea = get_object_or_404(
            ProjectIdea, pk=kwargs["idea_pk"], owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["idea"] = self.idea
        return context

    def get_success_url(self):
        return self.idea.get_absolute_url()


class MilestoneCreateView(IdeaOwnerMixin, SuccessMessageMixin, CreateView):
    form_class = MilestoneForm
    template_name = "ideas/milestone_form.html"
    success_message = "Milestone added."

    def form_valid(self, form):
        form.instance.idea = self.idea
        return super().form_valid(form)


class MilestoneUpdateView(IdeaOwnerMixin, SuccessMessageMixin, UpdateView):
    form_class = MilestoneForm
    template_name = "ideas/milestone_form.html"
    success_message = "Milestone updated."

    def get_queryset(self):
        return Milestone.objects.filter(idea=self.idea)


class MilestoneDeleteView(IdeaOwnerMixin, DeleteMessageMixin, DeleteView):
    template_name = "confirm_delete.html"
    success_message = "Milestone deleted."

    def get_queryset(self):
        return Milestone.objects.filter(idea=self.idea)
