from django.urls import path

from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.IdeaListView.as_view(), name="list"),
    path("mine/", views.MyIdeasView.as_view(), name="mine"),
    path("new/", views.IdeaCreateView.as_view(), name="create"),
    path("<int:pk>/", views.IdeaDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.IdeaUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.IdeaDeleteView.as_view(), name="delete"),
    path(
        "<int:idea_pk>/milestones/add/",
        views.MilestoneCreateView.as_view(),
        name="milestone_add",
    ),
    path(
        "<int:idea_pk>/milestones/<int:pk>/edit/",
        views.MilestoneUpdateView.as_view(),
        name="milestone_edit",
    ),
    path(
        "<int:idea_pk>/milestones/<int:pk>/delete/",
        views.MilestoneDeleteView.as_view(),
        name="milestone_delete",
    ),
]
