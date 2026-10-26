from django.utils import timezone
from rest_framework import serializers

from .models import Comment, Like, Post


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, user):
        profile = getattr(user, 'profile', None)
        if not profile or not profile.profile_image:
            return None
        request = self.context.get('request')
        url = profile.profile_image.url
        return request.build_absolute_uri(url) if request else url


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='user', read_only=True)
    likes_count = serializers.IntegerField(read_only=True, default=0)
    comments_count = serializers.IntegerField(read_only=True, default=0)
    is_liked = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'user', 'author', 'caption', 'image', 'scheduled_for', 'created_at',
            'is_published', 'likes_count', 'comments_count', 'is_liked',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'is_published']

    def validate_scheduled_for(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'username', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        like, created = Like.objects.get_or_create(user=user, post=validated_data['post'])
        if not created:
            raise serializers.ValidationError("You have already liked this post.")
        return like


class ReplySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'post', 'text', 'parent', 'created_at', 'updated_at']
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'username', 'post', 'text', 'parent', 'created_at', 'updated_at',
            'replies', 'replies_count',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        # Replies are one level deep, so a reply never has replies of its own.
        if obj.parent_id is not None:
            return []
        return ReplySerializer(obj.replies.all(), many=True, context=self.context).data

    def get_replies_count(self, obj):
        if obj.parent_id is not None:
            return 0
        return len(obj.replies.all())

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # A comment can be reworded, never moved to another post or thread.
        validated_data.pop('post', None)
        validated_data.pop('parent', None)
        return super().update(instance, validated_data)

    def validate(self, data):
        if self.instance is not None:
            return data
        parent = data.get('parent')
        if parent and parent.post_id != data['post'].id:
            raise serializers.ValidationError("Parent comment must belong to the same post.")
        if parent and parent.parent_id is not None:
            raise serializers.ValidationError("Replies can only be one level deep.")
        return data
