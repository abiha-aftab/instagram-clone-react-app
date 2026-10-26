from rest_framework import serializers

from .models import Story


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'title', 'content', 'media', 'created_at', 'expires_at', 'user']
        read_only_fields = ['user', 'created_at', 'expires_at']
