import pytest
from django.core.management import CommandError, call_command

from apps.posts.models import Post
from apps.stories.models import Story
from apps.users.models import User


@pytest.mark.django_db
def test_seed_demo_creates_a_browsable_feed(auth_client):
    call_command('seed_demo', password='Demo-only-1!')
    mara = User.objects.get(username='mara.okafor')
    assert mara.check_password('Demo-only-1!')
    assert Post.objects.count() == 8 and Story.objects.count() == 4
    assert all(post.image for post in Post.objects.all())

    feed = auth_client(mara).get('/api/posts/posts/').data
    assert feed['count'] == 8

    with pytest.raises(CommandError):
        call_command('seed_demo', password='Demo-only-1!')
