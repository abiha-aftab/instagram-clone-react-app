import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_schema_renders(api_client):
    response = api_client.get(reverse('schema'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_users_cannot_list_posts(api_client):
    response = api_client.get('/api/posts/posts/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_register_then_obtain_token(api_client):
    payload = {'email': 'ada@example.com', 'username': 'ada', 'password': 'Str0ng!pass'}
    assert api_client.post('/api/users/users/', payload, format='json').status_code == 201

    response = api_client.post(
        '/api/token/', {'email': 'ada@example.com', 'password': 'Str0ng!pass'}, format='json'
    )
    assert response.status_code == 200
    assert {'access', 'refresh'} <= response.data.keys()
