from rest_framework import serializers
from .models import Comment

# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = ['id', 'user', 'post', 'parent', 'content', 'created_at']
#         read_only_fields = ['user']


class CommentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent', 'content', 'created_at', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CommentSerializer(obj.children.all(), many=True).data
        return []
