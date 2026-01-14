from django.db import models

# Create your models here.


class Notification(models.Model):

    class Type(models.TextChoices):
        FOLLOW = 'follow'
        POST = 'post'
        LIKE = 'like'
        COMMENT = 'comment'
        Others = 'notifications'


    from_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    # optional
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_notifications')
    target_post = models.ForeignKey('posts.Post', null=True, blank=True, on_delete=models.CASCADE)
    target_comment = models.ForeignKey('posts.Comment', null=True, blank=True, on_delete=models.CASCADE)





    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=Type.choices)


    def __str__(self):
        return f'Notification from {self.from_user.username}: {self.message}'
    



# For Push Notifications
class PushSubscription(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    endpoint = models.TextField(unique=True)  # Browser push service URL
    p256dh = models.TextField()  # Public encryption key
    auth = models.TextField()    # Auth secret
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PushSubscription for {self.user.email}"
