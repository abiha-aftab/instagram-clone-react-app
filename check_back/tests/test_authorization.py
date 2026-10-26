import pytest

from apps.notifications.models import Notification
from apps.posts.models import Comment, Post
from apps.stories.models import Story


@pytest.fixture
def owner_and_intruder(auth_client):
    return auth_client(), auth_client()


@pytest.fixture
def post(owner_and_intruder):
    owner, _ = owner_and_intruder
    return Post.objects.create(user=owner.user, title='Original', caption='mine')


@pytest.mark.django_db
class TestPostOwnership:
    def test_owner_can_edit_and_delete(self, owner_and_intruder, post):
        owner, _ = owner_and_intruder
        url = f'/api/posts/posts/{post.id}/'
        assert owner.patch(url, {'caption': 'edited'}, format='json').status_code == 200
        assert owner.delete(url).status_code == 204

    def test_other_user_cannot_edit(self, owner_and_intruder, post):
        _, intruder = owner_and_intruder
        response = intruder.patch(f'/api/posts/posts/{post.id}/', {'caption': 'hijacked'}, format='json')
        assert response.status_code == 403
        assert 'your own' in response.data['detail']
        post.refresh_from_db()
        assert post.caption == 'mine'

    def test_other_user_cannot_delete(self, owner_and_intruder, post):
        _, intruder = owner_and_intruder
        assert intruder.delete(f'/api/posts/posts/{post.id}/').status_code == 403
        assert Post.objects.filter(pk=post.pk).exists()

    def test_other_user_can_still_read(self, owner_and_intruder, post):
        _, intruder = owner_and_intruder
        assert intruder.get(f'/api/posts/posts/{post.id}/').status_code == 200


@pytest.mark.django_db
class TestCommentOwnership:
    @pytest.fixture
    def comment(self, owner_and_intruder, post):
        owner, _ = owner_and_intruder
        return Comment.objects.create(user=owner.user, post=post, text='first!')

    def test_other_user_cannot_edit_or_delete(self, owner_and_intruder, comment):
        _, intruder = owner_and_intruder
        url = f'/api/posts/comments/{comment.id}/'
        assert intruder.patch(url, {'text': 'spam'}, format='json').status_code == 403
        assert intruder.delete(url).status_code == 403
        comment.refresh_from_db()
        assert comment.text == 'first!'

    def test_owner_edit_cannot_move_comment(self, owner_and_intruder, comment):
        owner, _ = owner_and_intruder
        other_post = Post.objects.create(user=owner.user, title='Other', caption='x')
        response = owner.patch(
            f'/api/posts/comments/{comment.id}/',
            {'text': 'reworded', 'post': other_post.id},
            format='json',
        )
        assert response.status_code == 200
        comment.refresh_from_db()
        assert (comment.text, comment.post_id) == ('reworded', comment.post_id)
        assert comment.post_id != other_post.id

    def test_owner_can_delete_reply(self, owner_and_intruder, comment):
        owner, _ = owner_and_intruder
        reply = Comment.objects.create(user=owner.user, post=comment.post, parent=comment, text='re')
        assert owner.delete(f'/api/posts/comments/{reply.id}/').status_code == 204


@pytest.mark.django_db
def test_story_requires_login_and_ownership(api_client, owner_and_intruder):
    owner, intruder = owner_and_intruder
    story = Story.objects.create(user=owner.user, title='Sunset', content='x')
    assert api_client.get('/api/stories/').status_code == 401
    assert intruder.delete(f'/api/stories/{story.id}/').status_code == 403
    assert owner.delete(f'/api/stories/{story.id}/').status_code == 204


@pytest.mark.django_db
def test_users_cannot_edit_or_delete_other_accounts(owner_and_intruder):
    owner, intruder = owner_and_intruder
    url = f'/api/users/users/{owner.user.id}/'
    assert intruder.patch(url, {'username': 'pwned'}, format='json').status_code == 403
    assert intruder.delete(url).status_code == 403
    assert owner.patch(url, {'username': 'renamed'}, format='json').status_code == 200


@pytest.mark.django_db
def test_notifications_are_private_and_cannot_be_forged(owner_and_intruder):
    owner, intruder = owner_and_intruder
    note = Notification.objects.create(
        from_user=intruder.user, to_user=owner.user, message='hi', notification_type='like'
    )
    assert intruder.get(f'/api/notifications/{note.id}/').status_code == 404
    assert intruder.post('/api/notifications/', {'message': 'fake'}, format='json').status_code == 405
    response = owner.patch(f'/api/notifications/{note.id}/', {'is_read': True}, format='json')
    assert response.status_code == 200 and response.data['is_read'] is True


@pytest.mark.django_db
def test_push_subscriptions_are_per_user(owner_and_intruder):
    owner, intruder = owner_and_intruder
    payload = {'endpoint': 'https://push.example.com/abc', 'p256dh': 'k', 'auth': 'a'}
    assert owner.post('/api/notifications/push-subscriptions/', payload, format='json').status_code == 201
    assert intruder.get('/api/notifications/push-subscriptions/').data == []
