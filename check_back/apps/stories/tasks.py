from celery import shared_task
from django.utils import timezone

from .models import Story


@shared_task
def purge_expired_stories():
    """Delete stories (and their media files) once their 24 hours are up."""
    expired = Story.objects.filter(expires_at__lte=timezone.now())
    count = 0
    for story in expired.iterator():
        if story.media:
            story.media.delete(save=False)
        story.delete()
        count += 1
    return count
