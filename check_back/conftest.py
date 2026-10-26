import shutil
import tempfile

import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def isolated_media(settings):
    media_root = tempfile.mkdtemp(prefix='instacham-media-')
    settings.MEDIA_ROOT = media_root
    yield
    shutil.rmtree(media_root, ignore_errors=True)


@pytest.fixture
def make_user(db, django_user_model):
    counter = {'n': 0}

    def _make_user(username=None, **extra):
        counter['n'] += 1
        username = username or f'user{counter["n"]}'
        return django_user_model.objects.create_user(
            email=f'{username}@example.com', username=username, password='Str0ng!pass', **extra
        )

    return _make_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(make_user):
    def _auth_client(user=None):
        user = user or make_user()
        client = APIClient()
        client.force_authenticate(user)
        client.user = user
        return client

    return _auth_client
