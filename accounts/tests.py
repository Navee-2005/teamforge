from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountTests(TestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newstudent",
                "email": "new@example.com",
                "password1": "Str0ng!Pass#2026",
                "password2": "Str0ng!Pass#2026",
            },
        )
        self.assertRedirects(
            response, reverse("accounts:profile_edit"), fetch_redirect_response=False
        )
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(hasattr(user, "profile"))

    def test_profile_update(self):
        user = User.objects.create_user("sam", password="pass12345")
        self.client.login(username="sam", password="pass12345")
        self.client.post(
            reverse("accounts:profile_edit"),
            {"department": "CSE", "skills_have": "Python, React"},
        )
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.department, "CSE")
        self.assertEqual(user.profile.have_list(), ["Python", "React"])
