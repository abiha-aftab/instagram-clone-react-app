from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Anyone authenticated may read; only the owner may change or delete."""

    message = 'You can only change or delete your own content.'
    owner_field = 'user'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, f'{self.owner_field}_id') == request.user.id


class IsSelfOrReadOnly(IsOwnerOrReadOnly):
    message = 'You can only change or delete your own account.'

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.pk == request.user.pk
