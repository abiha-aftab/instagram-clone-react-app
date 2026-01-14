from rest_framework import serializers
from django.utils import timezone
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'user', 'caption', 'image', 'scheduled_for', 'created_at', 'is_published']
        read_only_fields = ['id', 'created_at', 'is_published'] 

    def validate_scheduled_for(self, value):
        """Ensure scheduled_for is in the future."""
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request.user else None
        return Post.objects.create(user=user, **validated_data)