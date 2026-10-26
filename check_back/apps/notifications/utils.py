import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import PushSubscription

def send_web_push(user, payload):
    subs = PushSubscription.objects.filter(user=user)

    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    },
                },
                data=json.dumps(payload),
                vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
                vapid_claims={
                    "sub": f"mailto:{settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']}"
                },
            )
        except WebPushException:
            pass
