from rest_framework import serializers
from .models import Notification, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    from_username = serializers.CharField(source='from_user.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'from_user', 'from_username', 'to_user', 'message', 'is_read', 'created_at',
            'notification_type', 'target_post',
        ]
        read_only_fields = ['from_user', 'to_user', 'message', 'created_at', 'notification_type', 'target_post']


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

