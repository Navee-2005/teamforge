from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ideas.models import Milestone, ProjectIdea

User = get_user_model()
PASSWORD = "pass12345"


class IdeaTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password=PASSWORD)
        self.other = User.objects.create_user("other", password=PASSWORD)
        self.idea = ProjectIdea.objects.create(
            owner=self.owner,
            title="Crop Disease Detector",
            description="Detect disease from leaf photos",
            category="ai",
            level="advanced",
            required_skills="Python, Machine Learning",
            team_size=4,
        )

    def test_search_filters_results(self):
        ProjectIdea.objects.create(
            owner=self.other,
            title="Portfolio Builder",
            description="Static site generator",
            category="web",
            level="beginner",
            required_skills="HTML, CSS",
            team_size=3,
        )
        self.client.login(username="other", password=PASSWORD)
        response = self.client.get(reverse("ideas:list"), {"q": "Machine Learning"})
        self.assertContains(response, "Crop Disease Detector")
        self.assertNotContains(response, "Portfolio Builder")

    def test_only_owner_can_edit(self):
        self.client.login(username="other", password=PASSWORD)
        url = reverse("ideas:update", kwargs={"pk": self.idea.pk})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_progress_average(self):
        Milestone.objects.create(idea=self.idea, title="Dataset", progress=100)
        Milestone.objects.create(idea=self.idea, title="Model", progress=50)
        self.assertEqual(self.idea.overall_progress(), 75)

    def test_completed_milestone_sets_progress_100(self):
        milestone = Milestone.objects.create(
            idea=self.idea, title="Deploy", progress=10, is_completed=True
        )
        self.assertEqual(milestone.progress, 100)
