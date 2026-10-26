from rest_framework import serializers
from django.utils import timezone
from .models import Post, Like, Comment

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'user', 'caption', 'image', 'scheduled_for', 'created_at', 'is_published', 'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'created_at', 'is_published'] 

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False

    def validate_scheduled_for(self, value):
        """Ensure scheduled_for is in the future."""
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request.user else None
        return Post.objects.create(user=user, **validated_data)


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'username', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        
        # Check if already liked
        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            raise serializers.ValidationError("You have already liked this post.")
        return like


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'post', 'text', 'parent', 'created_at', 'updated_at', 'replies', 'replies_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        # Only return direct replies, not nested
        if obj.parent is None:
            replies = Comment.objects.filter(parent=obj).order_by('created_at')
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return Comment.objects.filter(parent=obj).count()
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return Comment.objects.create(**validated_data)
    
    def validate(self, data):
        # Ensure parent comment belongs to the same post
        parent = data.get('parent')
        post = data.get('post')
        if parent and parent.post != post:
            raise serializers.ValidationError("Parent comment must belong to the same post.")
        return data