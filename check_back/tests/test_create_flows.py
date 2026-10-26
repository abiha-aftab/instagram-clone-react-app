import pytest

from apps.notifications.models import Notification
from apps.posts.models import Post
from apps.stories.models import Story


@pytest.mark.django_db
def test_create_post_with_image(auth_client, png_upload):
    client = auth_client()
    response = client.post(
        '/api/posts/posts/',
        {'title': 'Harbour', 'caption': 'Morning light', 'image': png_upload()},
        format='multipart',
    )
    assert response.status_code == 201, response.data
    post = Post.objects.get()
    assert post.user == client.user
    assert post.image.name.startswith('posts/')


@pytest.mark.django_db
def test_post_owner_cannot_be_spoofed(auth_client, make_user):
    client = auth_client()
    other = make_user()
    response = client.post(
        '/api/posts/posts/', {'title': 'Mine', 'caption': 'x', 'user': other.id}, format='json'
    )
    assert response.status_code == 201
    assert Post.objects.get().user == client.user


@pytest.mark.django_db
def test_create_story_sets_24h_expiry(auth_client):
    client = auth_client()
    response = client.post(
        '/api/stories/', {'title': 'Lunch', 'content': 'Noodles'}, format='json'
    )
    assert response.status_code == 201, response.data
    story = Story.objects.get()
    assert story.user == client.user
    assert round((story.expires_at - story.created_at).total_seconds() / 3600) == 24


@pytest.mark.django_db
def test_like_notifies_author_but_not_self(auth_client, make_user):
    author = make_user()
    post = Post.objects.create(user=author, title='Hello', caption='x')

    auth_client(author).post(f'/api/posts/posts/{post.id}/like/')
    assert Notification.objects.count() == 0

    fan = auth_client()
    assert fan.post(f'/api/posts/posts/{post.id}/like/').status_code == 201
    notification = Notification.objects.get()
    assert (notification.from_user, notification.to_user) == (fan.user, author)


@pytest.mark.django_db
def test_new_user_gets_profile_with_nickname(make_user):
    user = make_user('grace')
    assert user.profile.nickname == 'grace'
