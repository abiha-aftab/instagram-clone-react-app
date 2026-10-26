# Django Urls with router
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', views.StoryViewSet, basename='story')


urlpatterns = router.urls
