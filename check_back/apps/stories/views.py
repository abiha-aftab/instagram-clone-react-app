from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.posts.queries import followed_user_ids
from core.permissions import IsOwnerOrReadOnly
from .models import Story
from .serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return (
            Story.objects.select_related('user')
            .filter(is_active=True, expires_at__gt=timezone.now())
            .filter(Q(user=user) | Q(user__in=followed_user_ids(user)))
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
