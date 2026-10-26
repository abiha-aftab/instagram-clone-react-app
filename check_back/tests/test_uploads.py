from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.posts.models import Post
from apps.stories.models import Story


def create_post(client, **fields):
    data = {'title': 'Pier', 'caption': 'x', **fields}
    return client.post('/api/posts/posts/', data, format='multipart')


@pytest.mark.django_db
class TestPostImageValidation:
    def test_rejects_file_that_is_not_an_image(self, auth_client):
        fake = SimpleUploadedFile('photo.png', b'definitely not a png', content_type='image/png')
        response = create_post(auth_client(), image=fake)
        assert response.status_code == 400
        assert 'image' in response.data
        assert not Post.objects.exists()

    def test_rejects_disallowed_extension(self, auth_client, png_upload):
        response = create_post(auth_client(), image=png_upload(name='photo.bmp.svg'))
        assert response.status_code == 400
        assert 'image' in response.data

    def test_rejects_oversized_image(self, auth_client, png_upload):
        upload = png_upload()
        padded = SimpleUploadedFile(
            'big.png', upload.read() + b'\0' * (5 * 1024 * 1024), content_type='image/png'
        )
        response = create_post(auth_client(), image=padded)
        assert response.status_code == 400
        assert 'too large' in str(response.data['image'])

    def test_accepts_small_png(self, auth_client, png_upload):
        assert create_post(auth_client(), image=png_upload()).status_code == 201

    def test_past_schedule_is_a_400_not_a_500(self, auth_client):
        past = (timezone.now() - timedelta(hours=1)).isoformat()
        response = create_post(auth_client(), scheduled_for=past)
        assert response.status_code == 400
        assert 'scheduled_for' in response.data


@pytest.mark.django_db
class TestStoryMediaValidation:
    def post_story(self, client, media):
        return client.post(
            '/api/stories/', {'title': 'Trip', 'content': 'x', 'media': media}, format='multipart'
        )

    def test_accepts_short_video(self, auth_client):
        clip = SimpleUploadedFile('clip.mp4', b'\0' * 1024, content_type='video/mp4')
        assert self.post_story(auth_client(), clip).status_code == 201
        assert Story.objects.get().media.name.endswith('.mp4')

    def test_rejects_executable(self, auth_client):
        payload = SimpleUploadedFile('run.sh', b'#!/bin/sh', content_type='text/x-sh')
        response = self.post_story(auth_client(), payload)
        assert response.status_code == 400
        assert 'Unsupported file type' in str(response.data['media'])

    def test_rejects_long_video(self, auth_client):
        clip = SimpleUploadedFile('long.webm', b'\0' * (25 * 1024 * 1024 + 1), content_type='video/webm')
        assert self.post_story(auth_client(), clip).status_code == 400
