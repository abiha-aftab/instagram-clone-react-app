# serializers for Notification model

from rest_framework import serializers
from .models import Notification, PushSubscription

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'from_user', 'to_user', 'message', 'is_read', 'created_at','notification_type']
        read_only_fields = ['from_user', 'to_user', 'created_at', 'notification_type']




class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['endpoint', 'p256dh', 'auth']  

    def create(self, validated_data):
        user = self.context['request'].user  
        subscription, _ = PushSubscription.objects.update_or_create(
            #lookup
            endpoint=validated_data['endpoint'], 
            defaults={**validated_data, 'user': user} 
        )
        return subscription

