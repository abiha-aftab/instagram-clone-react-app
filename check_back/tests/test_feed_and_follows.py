from datetime import timedelta

import pytest
from django.utils import timezone

from apps.notifications.models import Notification
from apps.posts.models import Post
from apps.stories.models import Story
from apps.stories.tasks import purge_expired_stories
from apps.users.models import Follow


def feed_titles(client):
    return [p['title'] for p in client.get('/api/posts/posts/').data['results']]


@pytest.mark.django_db
class TestFeed:
    def test_shows_own_and_followed_posts_only(self, auth_client, make_user):
        viewer = auth_client()
        friend, stranger = make_user(), make_user()
        Follow.objects.create(follower=viewer.user, following=friend)
        Post.objects.create(user=viewer.user, title='Mine', caption='x')
        Post.objects.create(user=friend, title='Friend', caption='x')
        stranger_post = Post.objects.create(user=stranger, title='Stranger', caption='x')

        assert sorted(feed_titles(viewer)) == ['Friend', 'Mine']
        assert viewer.get(f'/api/posts/posts/{stranger_post.id}/').status_code == 404

    def test_scheduled_posts_appear_once_due(self, auth_client, make_user):
        viewer = auth_client()
        friend = make_user()
        Follow.objects.create(follower=viewer.user, following=friend)
        later = Post.objects.create(
            user=friend, title='Later', caption='x', scheduled_for=timezone.now() + timedelta(hours=1)
        )
        assert feed_titles(viewer) == []

        Post.objects.filter(pk=later.pk).update(scheduled_for=timezone.now() - timedelta(minutes=1))
        assert feed_titles(viewer) == ['Later']

    def test_author_sees_own_scheduled_post_in_user_posts(self, auth_client):
        author = auth_client()
        response = author.post(
            '/api/posts/posts/',
            {'title': 'Soon', 'caption': 'x', 'scheduled_for': (timezone.now() + timedelta(days=1)).isoformat()},
            format='json',
        )
        assert response.status_code == 201 and response.data['is_published'] is False
        assert feed_titles(author) == []
        assert author.get('/api/posts/user-posts/').data['count'] == 1


@pytest.mark.django_db
class TestFollow:
    def test_follow_and_unfollow_update_counts(self, auth_client, make_user):
        viewer = auth_client()
        target = make_user('lin')
        url = f'/api/users/users/{target.id}/'

        assert viewer.post(url + 'follow/').status_code == 201
        assert viewer.post(url + 'follow/').status_code == 200
        data = viewer.get(url).data
        assert (data['followers_count'], data['is_following']) == (1, True)
        assert Notification.objects.filter(to_user=target, notification_type='follow').count() == 1

        me = viewer.get('/api/users/users/me/').data
        assert me['following_count'] == 1 and me['email'] == viewer.user.email

        assert viewer.post(url + 'unfollow/').status_code == 200
        assert viewer.get(url).data['followers_count'] == 0

    def test_cannot_follow_self(self, auth_client):
        viewer = auth_client()
        assert viewer.post(f'/api/users/users/{viewer.user.id}/follow/').status_code == 400

    def test_user_list_hides_emails_and_supports_search(self, auth_client, make_user):
        viewer = auth_client()
        make_user('marisol')
        results = viewer.get('/api/users/users/?search=maris').data['results']
        assert [u['username'] for u in results] == ['marisol']
        assert 'email' not in results[0]


@pytest.mark.django_db
class TestStories:
    def test_story_bar_shows_live_stories_of_followed_users(self, auth_client, make_user):
        viewer = auth_client()
        friend, stranger = make_user(), make_user()
        Follow.objects.create(follower=viewer.user, following=friend)
        Story.objects.create(user=friend, title='Live', content='x')
        Story.objects.create(user=stranger, title='Hidden', content='x')
        old = Story.objects.create(user=friend, title='Old', content='x')
        Story.objects.filter(pk=old.pk).update(expires_at=timezone.now() - timedelta(minutes=1))

        titles = [s['title'] for s in viewer.get('/api/stories/').data['results']]
        assert titles == ['Live']

    def test_purge_task_deletes_expired_stories(self, make_user):
        user = make_user()
        Story.objects.create(user=user, title='Fresh', content='x')
        old = Story.objects.create(user=user, title='Old', content='x')
        Story.objects.filter(pk=old.pk).update(expires_at=timezone.now() - timedelta(seconds=1))

        assert purge_expired_stories() == 1
        assert list(Story.objects.values_list('title', flat=True)) == ['Fresh']
