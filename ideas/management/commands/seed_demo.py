from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile
from collab.models import JoinRequest
from ideas.models import Milestone, ProjectIdea

DEMO_PASSWORD = "Demo@12345"

DEMO_USERS = [
    # username, department, year, skills have, skills want
    ("priya", "CSE", 4, "React, JavaScript, UI/UX", "Django, Docker"),
    ("ravi", "CSE", 3, "Python, Django, SQL", "React, Machine Learning"),
    ("sneha", "IT", 4, "Python, Machine Learning, Pandas", "Flask, Deployment"),
    ("arjun", "ECE", 3, "Arduino, IoT, C++", "Python, Django"),
]

DEMO_IDEAS = [
    # owner, title, description, category, level, skills, team size, hackathon
    ("priya", "Smart Attendance System",
     "Face-recognition based attendance with a Django dashboard for faculty.",
     "ai", "intermediate", "Python, OpenCV, Django", 4, "Smart India Hackathon"),
    ("ravi", "CampusConnect Events App",
     "A mobile-first events portal where clubs publish events and students RSVP.",
     "web", "beginner", "React, Django, UI/UX", 3, "College Hack Fest"),
    ("sneha", "Crop Disease Detector",
     "Upload a leaf photo and get a disease prediction with treatment tips.",
     "ai", "advanced", "Python, Machine Learning, Flask", 5, ""),
]


class Command(BaseCommand):
    help = "Create demo users, project ideas, a join request and milestones."

    def handle(self, *args, **options):
        User = get_user_model()
        users = {}
        for username, dept, year, have, want in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.com"}
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.department = dept
            profile.year_of_study = year
            profile.skills_have = have
            profile.skills_want = want
            profile.save()
            users[username] = user

        ideas = {}
        for owner, title, desc, cat, level, skills, size, event in DEMO_IDEAS:
            idea, _ = ProjectIdea.objects.get_or_create(
                owner=users[owner],
                title=title,
                defaults={
                    "description": desc,
                    "category": cat,
                    "level": level,
                    "required_skills": skills,
                    "team_size": size,
                    "hackathon_name": event,
                },
            )
            ideas[title] = idea

        JoinRequest.objects.get_or_create(
            idea=ideas["Smart Attendance System"],
            applicant=users["sneha"],
            defaults={"message": "I have built face-recognition models before."},
        )
        Milestone.objects.get_or_create(
            idea=ideas["Smart Attendance System"],
            title="Collect dataset",
            defaults={"progress": 60, "notes": "Gathered 40 student photos."},
        )

        self.stdout.write(self.style.SUCCESS("Demo data created."))
        self.stdout.write(f"Demo logins: priya / ravi / sneha / arjun  (password: {DEMO_PASSWORD})")
