from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/", views.UserPasswordChangeView.as_view(), name="password_change"),
    path(
        "password/done/",
        views.UserPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    path("profile/delete/", views.DeleteAccountView.as_view(), name="account_delete"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="profile_detail"),
    path("samples/add/", views.SampleCreateView.as_view(), name="sample_add"),
    path("samples/<int:pk>/delete/", views.SampleDeleteView.as_view(), name="sample_delete"),
]
