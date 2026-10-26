from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'push-subscriptions', views.PushSubscriptionViewSet, basename='push-subscription')
router.register(r'', views.NotificationViewSet, basename='notification')

urlpatterns = router.urls
