# myapp/tasks.py
from celery import shared_task
import time
import json
from pywebpush import webpush, WebPushException
from apps.notifications.models import PushSubscription

@shared_task
def add(x, y):
    time.sleep(5)  # simulate long-running task
    return x + y

@shared_task
def send_push_notification(user_id, message, title="Notification"):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    subscriptions = PushSubscription.objects.filter(user=user)
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=json.dumps({
                    "title": title,
                    "body": message,
                    "icon": "/icon.png",  # Add your icon
                }),
                vapid_private_key="your_vapid_private_key",  # Set in settings
                vapid_claims={
                    "sub": "mailto:your-email@example.com"
                }
            )
        except WebPushException as ex:
            print(f"Push failed: {ex}")
            # Optionally remove invalid subscription
