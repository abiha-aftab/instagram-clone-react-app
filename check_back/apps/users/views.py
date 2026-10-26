from django.db.models import Count, Exists, OuterRef, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsOwnerOrReadOnly, IsSelfOrReadOnly
from .models import Follow, Profile, User
from .serializers import (
    MeSerializer,
    ProfileSerializer,
    PublicUserSerializer,
    UpdateUserSerializer,
    UserSerializer,
)


def users_with_follow_stats(viewer):
    accepted = Q(followers__is_accepted=True)
    return (
        User.objects.filter(is_active=True)
        .select_related('profile')
        .annotate(
            followers_count=Count('followers', filter=accepted, distinct=True),
            following_count=Count('following', filter=Q(following__is_accepted=True), distinct=True),
            is_following=Exists(Follow.objects.filter(follower=viewer.pk, following=OuterRef('pk'))),
        )
        .order_by('username')
    )


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'

    def get_queryset(self):
        queryset = users_with_follow_stats(self.request.user)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return PublicUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('follow', 'unfollow'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSelfOrReadOnly()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.get_queryset().get(pk=request.user.pk)
        return Response(MeSerializer(user, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['post'])
    def follow(self, request, id=None):
        target = self.get_object()
        if target == request.user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        return Response(
            {'following': True, 'is_accepted': follow.is_accepted},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def unfollow(self, request, id=None):
        target = self.get_object()
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response({'following': False})


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
