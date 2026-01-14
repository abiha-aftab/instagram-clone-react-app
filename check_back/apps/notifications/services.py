from .models import Notification

def create_notification(
    *,
    from_user,
    to_user,
    notification_type,
    message,
    post=None,
    comment=None
):
    return Notification.objects.create(
        from_user=from_user,
        to_user=to_user,
        notification_type=notification_type,
        message=message,
        target_post=post,
        target_comment=comment
    )
