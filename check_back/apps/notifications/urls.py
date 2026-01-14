# Django Urls with router
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', views.NotificationViewSet, basename='notification')
router.register(r'push-subscription', views.PushSubscriptionViewSet, basename='push_subscription')



urlpatterns = router.urls
