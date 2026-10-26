from rest_framework import serializers
from .models import Story

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'title', 'content', 'created_at', 'expires_at', 'user']
        read_only_fields = ['user', 'created_at', 'expires_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request.user else None
        return Story.objects.create(user=user, **validated_data)