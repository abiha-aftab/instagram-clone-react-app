import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.posts.models import Comment, Like, Post


def count_queries(client, url):
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200
    return len(ctx.captured_queries), response.data


def add_posts(author, fans, n):
    for i in range(n):
        post = Post.objects.create(user=author, title=f'Post {i}', caption='x')
        for fan in fans:
            Like.objects.create(user=fan, post=post)
            Comment.objects.create(user=fan, post=post, text='nice')


@pytest.mark.django_db
def test_feed_query_count_does_not_grow_with_posts(auth_client, make_user):
    viewer = auth_client()
    author, fans = make_user(), [make_user(), make_user()]

    add_posts(author, fans, 2)
    small, _ = count_queries(viewer, '/api/posts/posts/')
    add_posts(author, fans, 8)
    large, data = count_queries(viewer, '/api/posts/posts/')

    assert large == small <= 3
    first = data['results'][0]
    assert (first['likes_count'], first['comments_count'], first['is_liked']) == (2, 2, False)
    assert first['author']['username'] == author.username


@pytest.mark.django_db
def test_is_liked_reflects_the_viewer(auth_client, make_user):
    viewer = auth_client()
    post = Post.objects.create(user=make_user(), title='Hi', caption='x')
    Like.objects.create(user=viewer.user, post=post)
    assert viewer.get(f'/api/posts/posts/{post.id}/').data['is_liked'] is True


@pytest.mark.django_db
def test_comment_thread_query_count_is_constant(auth_client, make_user):
    client = auth_client()
    post = Post.objects.create(user=client.user, title='Thread', caption='x')

    def add_thread():
        top = Comment.objects.create(user=make_user(), post=post, text='top')
        for _ in range(3):
            Comment.objects.create(user=make_user(), post=post, parent=top, text='reply')

    add_thread()
    small, _ = count_queries(client, f'/api/posts/posts/{post.id}/comments/')
    for _ in range(5):
        add_thread()
    large, data = count_queries(client, f'/api/posts/posts/{post.id}/comments/')

    assert large == small
    assert data['results'][0]['replies_count'] == 3
    assert len(data['results'][0]['replies']) == 3


@pytest.mark.django_db
def test_replies_cannot_be_nested_twice(auth_client):
    client = auth_client()
    post = Post.objects.create(user=client.user, title='Thread', caption='x')
    top = Comment.objects.create(user=client.user, post=post, text='top')
    reply = Comment.objects.create(user=client.user, post=post, parent=top, text='reply')
    response = client.post(
        '/api/posts/comments/', {'post': post.id, 'parent': reply.id, 'text': 'deeper'}, format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_response_includes_zeroed_stats(auth_client):
    response = auth_client().post('/api/posts/posts/', {'title': 'New', 'caption': 'x'}, format='json')
    assert response.status_code == 201
    assert (response.data['likes_count'], response.data['is_liked']) == (0, False)
