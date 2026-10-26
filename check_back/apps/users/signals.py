# signal for user creation
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Profile, Follow
from ..posts.models import Like, Comment
from ..notifications.models import Notification
from core.tasks import send_push_notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile for the new user
        Profile.objects.create(user=instance)
        # TODO: trigger an alert or log creation
        print(f"New profile created for {instance.email}")

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        if instance.following.is_public:
            # Direct follow
            message = f"{instance.follower.username} started following you."
            notification_type = Notification.Type.FOLLOW
        else:
            # Follow request
            message = f"{instance.follower.username} sent you a follow request."
            notification_type = Notification.Type.FOLLOW
        Notification.objects.create(
            from_user=instance.follower,
            to_user=instance.following,
            message=message,
            notification_type=notification_type
        )
        # Send push notification
        send_push_notification.delay(instance.following.id, message, "New Follower")

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        message = f"{instance.user.username} liked your post '{instance.post.title}'."
        Notification.objects.create(
            from_user=instance.user,
            to_user=instance.post.user,
            target_post=instance.post,
            message=message,
            notification_type=Notification.Type.LIKE
        )
        send_push_notification.delay(instance.post.user.id, message, "New Like")

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        if instance.parent:
            # Reply to comment
            to_user = instance.parent.user
            message = f"{instance.user.username} replied to your comment."
        else:
            # Comment on post
            to_user = instance.post.user
            message = f"{instance.user.username} commented on your post '{instance.post.title}'."
        Notification.objects.create(
            from_user=instance.user,
            to_user=to_user,
            target_post=instance.post,
            target_comment=instance,
            message=message,
            notification_type=Notification.Type.COMMENT
        )
        send_push_notification.delay(to_user.id, message, "New Comment")
