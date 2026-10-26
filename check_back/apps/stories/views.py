from django.shortcuts import render

# Create your views here.
from .models import Story
from .serializers import StorySerializer

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    # instances chaa raha bacha
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
