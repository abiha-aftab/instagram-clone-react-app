import pytest

from apps.posts.models import Comment, Like, Post


@pytest.fixture
def client_with_posts(auth_client):
    client = auth_client()
    Post.objects.bulk_create(
        Post(user=client.user, title=f'Post {i}', caption='x') for i in range(23)
    )
    return client


@pytest.mark.django_db
def test_feed_is_paginated_newest_first(client_with_posts):
    first = client_with_posts.get('/api/posts/posts/').data
    assert first['count'] == 23
    assert len(first['results']) == 10
    assert first['next'] and first['previous'] is None

    last = client_with_posts.get('/api/posts/posts/?page=3').data
    assert len(last['results']) == 3
    assert last['next'] is None

    ids = [p['id'] for p in first['results']]
    assert ids == sorted(ids, reverse=True)


@pytest.mark.django_db
def test_page_size_is_capped(client_with_posts):
    assert len(client_with_posts.get('/api/posts/posts/?page_size=5').data['results']) == 5
    response = client_with_posts.get('/api/posts/posts/?page_size=1000')
    assert len(response.data['results']) == 23  # capped at 50, only 23 exist


@pytest.mark.django_db
def test_out_of_range_page_is_404(client_with_posts):
    assert client_with_posts.get('/api/posts/posts/?page=99').status_code == 404


@pytest.mark.django_db
def test_post_comments_and_likes_are_paginated(auth_client, make_user):
    client = auth_client()
    post = Post.objects.create(user=client.user, title='Busy', caption='x')
    for i in range(12):
        Comment.objects.create(user=client.user, post=post, text=f'c{i}')
        Like.objects.create(user=make_user(), post=post)

    comments = client.get(f'/api/posts/posts/{post.id}/comments/').data
    assert comments['count'] == 12 and len(comments['results']) == 10
    likes = client.get(f'/api/posts/posts/{post.id}/likes/?page=2').data
    assert likes['count'] == 12 and len(likes['results']) == 2
