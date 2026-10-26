import pytest

from apps.notifications.models import Notification


@pytest.mark.django_db
def test_unread_filter_and_mark_all_read(auth_client, make_user):
    me = auth_client()
    other = make_user()
    for i in range(3):
        Notification.objects.create(
            from_user=other, to_user=me.user, message=f'n{i}', notification_type='like'
        )
    Notification.objects.create(from_user=me.user, to_user=other, message='theirs', notification_type='like')

    assert me.get('/api/notifications/?unread=1').data['count'] == 3
    assert me.post('/api/notifications/mark-all-read/').data == {'marked_read': 3}
    assert me.get('/api/notifications/?unread=1').data['count'] == 0
    assert Notification.objects.get(to_user=other).is_read is False


@pytest.mark.django_db
def test_notification_names_the_sender(auth_client, make_user):
    me = auth_client()
    sender = make_user('kofi')
    Notification.objects.create(from_user=sender, to_user=me.user, message='hi', notification_type='follow')
    assert me.get('/api/notifications/').data['results'][0]['from_username'] == 'kofi'
