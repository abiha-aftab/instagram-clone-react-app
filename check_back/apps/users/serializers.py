import re

from rest_framework import serializers

from .models import Follow, Profile, User


class BaseUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*()\-+=_.,?]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate_email(self, value):
        value = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_username(self, value):
        taken = User.objects.filter(username__iexact=value)
        if self.instance is not None:
            taken = taken.exclude(pk=self.instance.pk)
        if taken.exists():
            raise serializers.ValidationError("Username is already in use.")
        return value


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'is_active']
        read_only_fields = ['is_active']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UpdateUserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active']
        read_only_fields = ['email', 'is_active']


class PublicUserSerializer(serializers.ModelSerializer):
    """What other people may see about an account: no email."""

    nickname = serializers.CharField(source='profile.nickname', read_only=True)
    bio = serializers.CharField(source='profile.bio', read_only=True)
    avatar = serializers.ImageField(source='profile.profile_image', read_only=True)
    followers_count = serializers.IntegerField(read_only=True, default=0)
    following_count = serializers.IntegerField(read_only=True, default=0)
    is_following = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'bio', 'avatar', 'is_public',
            'followers_count', 'following_count', 'is_following',
        ]


class MeSerializer(PublicUserSerializer):
    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + ['email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'nickname', 'bio', 'profile_image', 'created_at']
        read_only_fields = ['user', 'created_at']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'is_accepted', 'created_at']
