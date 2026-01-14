import re
from django.db import models
from django.contrib.auth.models import  BaseUserManager
from rest_framework import serializers
from .models import User, Profile, Follow


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
        if not re.search(r'[!@#$%^&*()-+=]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value
    
    def validate_email(self, value):
        # normalize email
        value = self.Meta.model.objects.normalize_email(value)
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value
    


class UserSerializer(BaseUserSerializer ):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'is_active']


    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
         


class UpdateUserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active']
        read_only_fields = ['email']

    
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'nickname', 'bio', 'profile_image', 'created_at']
 

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']





