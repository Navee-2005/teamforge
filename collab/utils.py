from .models import Notification


def notify(recipient, message, link=""):
    """Create an in-app notification."""
    return Notification.objects.create(
        recipient=recipient, message=message[:255], link=link
    )
