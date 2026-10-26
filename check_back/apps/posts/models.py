from django.db import models
from django.core.validators import MinLengthValidator as Mi
from cloudinary.models import CloudinaryField
from django.utils import timezone
# Create your models here.

def validate_scheduled_for(value):
    if value and value < timezone.now():
        raise models.ValidationError("Scheduled time must be in the future.")
    

class Post(models.Model):
    title = models.CharField(max_length=255, validators=[Mi(2)])
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    caption = models.TextField()
    image = CloudinaryField('media', blank=True, null=True)
    scheduled_for = models.DateTimeField(null=True, blank=True, validators=[validate_scheduled_for])
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)


    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


class Comment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    @property
    def is_reply(self):
        return self.parent is not None