# Django Urls with router
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'user-posts', views.OwnPostViewSet, basename='user-post')
router.register(r'likes', views.LikeViewSet, basename='like')
router.register(r'comments', views.CommentViewSet, basename='comment')


urlpatterns = router.urls
