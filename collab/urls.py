from django.urls import path

from . import views

app_name = "collab"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("requests/incoming/", views.IncomingRequestsView.as_view(), name="incoming"),
    path("requests/outgoing/", views.OutgoingRequestsView.as_view(), name="outgoing"),
    path("requests/apply/<int:idea_pk>/", views.ApplyView.as_view(), name="apply"),
    path("requests/<int:pk>/accept/", views.AcceptRequestView.as_view(), name="accept"),
    path("requests/<int:pk>/reject/", views.RejectRequestView.as_view(), name="reject"),
    path("requests/<int:pk>/cancel/", views.CancelRequestView.as_view(), name="cancel"),
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("notifications/read-all/", views.MarkAllReadView.as_view(), name="read_all"),
    path(
        "notifications/<int:pk>/read/",
        views.MarkNotificationReadView.as_view(),
        name="read",
    ),
]
