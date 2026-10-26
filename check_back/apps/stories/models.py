from datetime import timedelta
from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.
class Story(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='stories')    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    media = CloudinaryField('media', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['expires_at']),
        ]


    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=24) 
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title
    