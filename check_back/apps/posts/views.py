from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
# Create your views here.


from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user else None)
    
    @action(detail=True, methods=['post'], url_path='like')
    def like_post(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'You have already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='unlike')
    def unlike_post(self, request, pk=None):
        """Unlike a post"""
        post = self.get_object()
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'message': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='likes')
    def get_likes(self, request, pk=None):
        """Get all likes for a post"""
        post = self.get_object()
        likes = Like.objects.filter(post=post).select_related('user')
        serializer = LikeSerializer(likes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='comments')
    def get_comments(self, request, pk=None):
        """Get all top-level comments for a post"""
        post = self.get_object()
        comments = Comment.objects.filter(post=post, parent=None).order_by('created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class OwnPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        user = self.request.user
        if user is None or not user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.") 
        serializer.save(user=user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by('-created_at')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        queryset = Like.objects.all().select_related('user', 'post')
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        like = self.get_object()
        if like.user != request.user:
            raise PermissionDenied("You can only delete your own likes.")
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Comment.objects.all().select_related('user', 'post', 'parent')
        post_id = self.request.query_params.get('post', None)
        parent_id = self.request.query_params.get('parent', None)
        
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif parent_id is None and post_id:
            # Only top-level comments
            queryset = queryset.filter(parent=None)
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            raise PermissionDenied("You can only edit your own comments.")
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            raise PermissionDenied("You can only delete your own comments.")
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'], url_path='replies')
    def get_replies(self, request, pk=None):
        """Get all replies for a comment"""
        comment = self.get_object()
        replies = Comment.objects.filter(parent=comment).order_by('created_at')
        serializer = CommentSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)

