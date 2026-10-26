from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsOwnerOrReadOnly
from .models import Comment, Like, Post
from .queries import comments_with_replies, posts_with_stats, published_filter, visible_posts
from .serializers import CommentSerializer, LikeSerializer, PostSerializer


class PaginatedActionsMixin:
    def paginated_response(self, queryset, serializer_class):
        page = self.paginate_queryset(queryset)
        serializer = serializer_class(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


class PostViewSet(PaginatedActionsMixin, viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        queryset = visible_posts(self.request.user)
        if self.action == 'list':
            # The feed shows scheduled posts only once their time has come.
            queryset = queryset.filter(published_filter())
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='like', permission_classes=[IsAuthenticated])
    def like_post(self, request, pk=None):
        post = self.get_object()
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'You have already liked this post'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='unlike', permission_classes=[IsAuthenticated])
    def unlike_post(self, request, pk=None):
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
        return Response({'message': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='likes')
    def get_likes(self, request, pk=None):
        post = self.get_object()
        likes = Like.objects.filter(post=post).select_related('user').order_by('-created_at')
        return self.paginated_response(likes, LikeSerializer)

    @action(detail=True, methods=['get'], url_path='comments')
    def get_comments(self, request, pk=None):
        post = self.get_object()
        comments = comments_with_replies().filter(post=post, parent=None).order_by('created_at')
        return self.paginated_response(comments, CommentSerializer)


class OwnPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return posts_with_stats(self.request.user).filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        queryset = Like.objects.select_related('user')
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own likes.")
        instance.delete()


class CommentViewSet(PaginatedActionsMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = comments_with_replies()
        post_id = self.request.query_params.get('post')
        parent_id = self.request.query_params.get('parent')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif post_id:
            queryset = queryset.filter(parent=None)
        return queryset.order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='replies')
    def get_replies(self, request, pk=None):
        comment = self.get_object()
        replies = comments_with_replies().filter(parent=comment).order_by('created_at')
        return self.paginated_response(replies, CommentSerializer)
