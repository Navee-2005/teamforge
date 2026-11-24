from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from collab.models import JoinRequest, Notification
from ideas.models import ProjectIdea

User = get_user_model()
PASSWORD = "pass12345"


class CollabFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password=PASSWORD)
        self.member = User.objects.create_user("member", password=PASSWORD)
        self.idea = ProjectIdea.objects.create(
            owner=self.owner,
            title="Smart Attendance",
            description="Face recognition attendance",
            category="ai",
            level="beginner",
            required_skills="Python, OpenCV",
            team_size=2,  # owner + 1 teammate
        )

    def test_profile_created_automatically(self):
        self.assertTrue(hasattr(self.owner, "profile"))

    def test_pages_require_login(self):
        url = reverse("ideas:list")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_apply_accept_closes_team(self):
        self.client.login(username="member", password=PASSWORD)
        response = self.client.post(
            reverse("collab:apply", kwargs={"idea_pk": self.idea.pk}),
            {"message": "I know Python"},
        )
        self.assertRedirects(
            response, reverse("collab:outgoing"), fetch_redirect_response=False
        )
        join_request = JoinRequest.objects.get(idea=self.idea, applicant=self.member)
        self.assertEqual(join_request.status, "pending")
        self.assertEqual(Notification.objects.filter(recipient=self.owner).count(), 1)

        self.client.logout()
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(reverse("collab:accept", kwargs={"pk": join_request.pk}))
        join_request.refresh_from_db()
        self.idea.refresh_from_db()
        self.assertEqual(join_request.status, "accepted")
        self.assertEqual(self.idea.status, "closed")
        self.assertEqual(Notification.objects.filter(recipient=self.member).count(), 1)

    def test_owner_cannot_apply_to_own_idea(self):
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(
            reverse("collab:apply", kwargs={"idea_pk": self.idea.pk}),
            {"message": "me"},
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_cancel_request(self):
        join_request = JoinRequest.objects.create(
            idea=self.idea, applicant=self.member, message="hi"
        )
        self.client.login(username="member", password=PASSWORD)
        self.client.post(reverse("collab:cancel", kwargs={"pk": join_request.pk}))
        join_request.refresh_from_db()
        self.assertEqual(join_request.status, "cancelled")
