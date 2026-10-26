from django.db.models import Count, Exists, OuterRef, Prefetch, Value

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
