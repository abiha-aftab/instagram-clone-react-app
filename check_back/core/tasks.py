from celery import shared_task
from django.contrib.auth import get_user_model

from apps.notifications.utils import send_web_push


@shared_task
def send_push_notification(user_id, message, title='Notification'):
    user = get_user_model().objects.filter(id=user_id).first()
    if user is None:
        return
    send_web_push(user, {'title': title, 'body': message})
