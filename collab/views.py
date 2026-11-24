from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from ideas.models import ProjectIdea
from ideas.utils import match_ideas_for

from .forms import JoinRequestForm
from .models import JoinRequest, Notification
from .utils import notify


def safe_next(request, default):
    """Redirect target from POST 'next', only if it stays on this site."""
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}
    ):
        return target
    return default


# --------------------------------------------------------------------------
# Landing page + dashboard
# --------------------------------------------------------------------------
class HomeView(TemplateView):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("collab:dashboard")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "collab/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        incoming = JoinRequest.objects.filter(idea__owner=user)
        outgoing = JoinRequest.objects.filter(applicant=user)
        context.update(
            {
                "total_ideas": ProjectIdea.objects.count(),
                "open_ideas": ProjectIdea.objects.filter(status="open").count(),
                "my_ideas_count": ProjectIdea.objects.filter(owner=user).count(),
                "pending_incoming": incoming.filter(status=JoinRequest.PENDING).count(),
                "pending_outgoing": outgoing.filter(status=JoinRequest.PENDING).count(),
                "accepted_total": JoinRequest.objects.filter(
                    status=JoinRequest.ACCEPTED
                )
                .filter(Q(applicant=user) | Q(idea__owner=user))
                .count(),
                "recent_ideas": ProjectIdea.objects.select_related("owner")[:5],
                "recent_notifications": Notification.objects.filter(recipient=user)[:5],
                "matches": match_ideas_for(user),
                "my_teams": ProjectIdea.objects.filter(
                    join_requests__applicant=user,
                    join_requests__status=JoinRequest.ACCEPTED,
                ).select_related("owner"),
            }
        )
        return context


# --------------------------------------------------------------------------
# Join requests
# --------------------------------------------------------------------------
class ApplyView(LoginRequiredMixin, CreateView):
    form_class = JoinRequestForm
    template_name = "collab/request_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.idea = get_object_or_404(ProjectIdea, pk=kwargs["idea_pk"])
        if self.idea.owner_id == request.user.id:
            messages.error(request, "You cannot apply to your own project.")
            return redirect(self.idea)
        if self.idea.status != "open" or self.idea.is_full():
            messages.error(request, "This team is no longer accepting members.")
            return redirect(self.idea)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["idea"] = self.idea
        return context

    def form_valid(self, form):
        user = self.request.user
        existing = JoinRequest.objects.filter(idea=self.idea, applicant=user).first()
        if existing and existing.status != JoinRequest.CANCELLED:
            messages.warning(self.request, "You have already applied to this project.")
            return redirect(self.idea)
        if existing:  # re-apply after cancelling
            existing.message = form.cleaned_data["message"]
            existing.status = JoinRequest.PENDING
            existing.save()
            self.object = existing
        else:
            form.instance.idea = self.idea
            form.instance.applicant = user
            self.object = form.save()
        notify(
            self.idea.owner,
            f"{user.username} wants to join your project '{self.idea.title}'.",
            reverse("collab:incoming"),
        )
        messages.success(self.request, "Request sent! The owner has been notified.")
        return redirect("collab:outgoing")


class RequestListBase(LoginRequiredMixin, ListView):
    template_name = "collab/request_list.html"
    context_object_name = "join_requests"
    paginate_by = 10
    mode = ""

    def base_queryset(self):
        raise NotImplementedError

    def get_queryset(self):
        qs = self.base_queryset().select_related(
            "idea", "applicant", "applicant__profile", "idea__owner"
        )
        status = self.request.GET.get("status", "")
        if status in dict(JoinRequest.STATUS_CHOICES):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "mode": self.mode,
                "status_choices": JoinRequest.STATUS_CHOICES,
                "selected_status": self.request.GET.get("status", ""),
                "querystring": params.urlencode(),
            }
        )
        return context


class IncomingRequestsView(RequestListBase):
    mode = "incoming"

    def base_queryset(self):
        return JoinRequest.objects.filter(idea__owner=self.request.user)


class OutgoingRequestsView(RequestListBase):
    mode = "outgoing"

    def base_queryset(self):
        return JoinRequest.objects.filter(applicant=self.request.user)


class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        join_request = get_object_or_404(
            JoinRequest.objects.select_related("idea", "applicant"),
            pk=pk,
            idea__owner=request.user,
        )
        idea = join_request.idea
        if join_request.status != JoinRequest.PENDING:
            messages.warning(request, "This request has already been handled.")
        elif idea.is_full():
            messages.error(request, "Your team is already full.")
        else:
            join_request.status = JoinRequest.ACCEPTED
            join_request.save()
            if idea.is_full():  # last spot taken -> close recruiting
                idea.status = "closed"
                idea.save()
            notify(
                join_request.applicant,
                f"Your request to join '{idea.title}' was accepted!",
                idea.get_absolute_url(),
            )
            messages.success(request, f"{join_request.applicant.username} joined your team.")
        return redirect(safe_next(request, reverse("collab:incoming")))


class RejectRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        join_request = get_object_or_404(
            JoinRequest.objects.select_related("idea", "applicant"),
            pk=pk,
            idea__owner=request.user,
        )
        if join_request.status != JoinRequest.PENDING:
            messages.warning(request, "This request has already been handled.")
        else:
            join_request.status = JoinRequest.REJECTED
            join_request.save()
            notify(
                join_request.applicant,
                f"Your request to join '{join_request.idea.title}' was declined.",
                join_request.idea.get_absolute_url(),
            )
            messages.info(request, "Request rejected.")
        return redirect(safe_next(request, reverse("collab:incoming")))


class CancelRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        join_request = get_object_or_404(
            JoinRequest.objects.select_related("idea", "applicant"),
            pk=pk,
            applicant=request.user,
        )
        idea = join_request.idea
        if join_request.status not in (JoinRequest.PENDING, JoinRequest.ACCEPTED):
            messages.warning(request, "This request can no longer be cancelled.")
        else:
            was_accepted = join_request.status == JoinRequest.ACCEPTED
            join_request.status = JoinRequest.CANCELLED
            join_request.save()
            if was_accepted and idea.status == "closed" and not idea.is_full():
                idea.status = "open"  # a spot is free again
                idea.save()
            notify(
                idea.owner,
                f"{request.user.username} cancelled their request for '{idea.title}'.",
                reverse("collab:incoming"),
            )
            messages.info(request, "Request cancelled.")
        return redirect("collab:outgoing")


# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------
class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "collab/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return redirect(notification.link or "collab:notifications")


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True
        )
        messages.success(request, "All notifications marked as read.")
        return redirect("collab:notifications")
