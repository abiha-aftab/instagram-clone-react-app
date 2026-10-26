from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import IsOwnerOrReadOnly, IsSelfOrReadOnly
from .models import Profile, User
from .serializers import ProfileSerializer, UpdateUserSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsSelfOrReadOnly()]


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
