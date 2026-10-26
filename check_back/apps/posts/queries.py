from django.db.models import Count, Exists, OuterRef, Prefetch, Q, Value
from django.utils import timezone

from apps.users.models import Follow
from .models import Comment, Like, Post


def posts_with_stats(user):
    """Posts with author, counts and the viewer's like state fetched in one query."""
    if user.is_authenticated:
        liked_by_viewer = Exists(Like.objects.filter(post=OuterRef('pk'), user=user))
    else:
        liked_by_viewer = Value(False)
    return (
        Post.objects.select_related('user__profile')
        .annotate(
            likes_count=Count('like', distinct=True),
            comments_count=Count('comment', distinct=True),
            is_liked=liked_by_viewer,
        )
        .order_by('-created_at')
    )


def comments_with_replies():
    """Comments with their author and one level of replies prefetched."""
    replies = Comment.objects.select_related('user').order_by('created_at')
    return Comment.objects.select_related('user').prefetch_related(
        Prefetch('replies', queryset=replies)
    )


def published_filter():
    return Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now())


def followed_user_ids(user):
    return Follow.objects.filter(follower=user, is_accepted=True).values('following')


def visible_posts(user):
    """Your own posts (scheduled or not) plus published posts of people you follow."""
    followed_and_published = Q(user__in=followed_user_ids(user)) & published_filter()
    return posts_with_stats(user).filter(Q(user=user) | followed_and_published)
