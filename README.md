# TeamForge - Hackathon Team Finder (Django)

Students publish project ideas, find teammates by skill, apply to teams and
track progress together.

## Run it

    python -m venv venv
    venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
    pip install -r requirements.txt
    python manage.py makemigrations accounts ideas collab
    python manage.py migrate
    python manage.py seed_demo      # optional demo data
    python manage.py createsuperuser
    python manage.py test           # optional: run the automated tests
    python manage.py runserver

Open http://127.0.0.1:8000/  (admin: /admin/)
Demo logins after seed_demo: priya / ravi / sneha / arjun, password Demo@12345

## Assignment module mapping

| Module                    | Where                                   |
|---------------------------|-----------------------------------------|
| User Authentication       | accounts (register, login, logout, password change) |
| Student Profile           | accounts (Profile, ProfileSample)       |
| Skill Marketplace         | ideas (ProjectIdea CRUD, search, filter, pagination) |
| Mentorship Requests       | collab (JoinRequest: apply, accept, reject, cancel) |
| Learning Tracker          | ideas (Milestone progress tracker)      |
| Dashboard & Notifications | collab (DashboardView, Notification)    |
