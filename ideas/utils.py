"""Skill-matching helpers (the 'advanced' feature of TeamForge)."""
from accounts.models import Profile

from .models import ProjectIdea


def skill_set(text):
    return {s.strip().lower() for s in (text or "").split(",") if s.strip()}


def match_ideas_for(user, limit=5):
    """Open ideas (not mine) whose required skills overlap the skills I have."""
    mine = skill_set(user.profile.skills_have)
    if not mine:
        return []
    results = []
    ideas = (
        ProjectIdea.objects.filter(status="open")
        .exclude(owner=user)
        .select_related("owner")[:100]
    )
    for idea in ideas:
        overlap = mine & skill_set(idea.required_skills)
        if overlap:
            results.append({"idea": idea, "skills": sorted(overlap)})
    results.sort(key=lambda item: -len(item["skills"]))
    return results[:limit]


def match_people_for(idea, limit=5):
    """Profiles whose skills overlap what this idea needs."""
    needed = skill_set(idea.required_skills)
    if not needed:
        return []
    results = []
    profiles = Profile.objects.exclude(user=idea.owner).select_related("user")[:200]
    for profile in profiles:
        overlap = needed & skill_set(profile.skills_have)
        if overlap:
            results.append({"profile": profile, "skills": sorted(overlap)})
    results.sort(key=lambda item: -len(item["skills"]))
    return results[:limit]
