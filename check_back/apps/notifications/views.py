from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user).order_by('-created_at')




class PushSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user).order_by('-created_at')


      
