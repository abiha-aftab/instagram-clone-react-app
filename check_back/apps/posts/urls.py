# Django Urls with router
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', views.PostViewSet, basename='post')
router.register(r'user-posts', views.PostViewSet, basename='user-post')


urlpatterns = router.urls
