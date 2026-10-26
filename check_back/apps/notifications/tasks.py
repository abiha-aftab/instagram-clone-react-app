from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import send_web_push

User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={'max_retries': 3})
def send_push_task(self, user_id, payload):
    user = User.objects.get(id=user_id)
    send_web_push(user, payload)
