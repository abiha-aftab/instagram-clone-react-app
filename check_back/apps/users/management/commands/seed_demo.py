"""Fill an empty database with fictional people, posts and stories for demos."""

import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw

from apps.posts.models import Comment, Like, Post
from apps.stories.models import Story
from apps.users.models import Follow, User

PEOPLE = [
    ('mara.okafor', 'Mara', 'Film photographer. Mostly harbours and fog.'),
    ('teo.lindqvist', 'Teo', 'Cycling, bread, long shadows.'),
    ('ines.duarte', 'Ines', 'Tiles, terraces and too much coffee.'),
    ('kai.nakamura', 'Kai', 'Night walks with a 35mm.'),
    ('zuri.mensah', 'Zuri', 'Market colours and street food.'),
]

POSTS = [
    ('Low tide', 'The harbour at 6am, before anyone else showed up.'),
    ('Terracotta', 'Rooftops on the walk home.'),
    ('Night ferry', 'Last crossing of the evening.'),
    ('Citrus stall', 'Saturday market, best oranges in town.'),
    ('Fog bank', 'Could not see the bridge at all.'),
    ('Long shadow', 'Golden hour on the cycle path.'),
    ('Blue door', 'Found this one on a side street.'),
    ('Steam', 'Noodle bar window, 11pm.'),
]

COMMENTS = ['This light is unreal', 'Where is this?', 'Saving this one', 'Colours!', 'Need to go here']

PALETTES = [
    ('#1f3b4d', '#e07a5f', '#f2cc8f'),
    ('#264653', '#2a9d8f', '#e9c46a'),
    ('#3d405b', '#81b29a', '#f4f1de'),
    ('#2b2d42', '#ef8354', '#bfc0c0'),
    ('#283618', '#dda15e', '#fefae0'),
]


def render_scene(seed, size=900):
    """A simple generated landscape: sky band, sun, layered hills."""
    rng = random.Random(seed)
    dark, accent, light = PALETTES[seed % len(PALETTES)]
    image = Image.new('RGB', (size, size), light)
    draw = ImageDraw.Draw(image)
    sun_x, sun_r = rng.randint(200, 700), rng.randint(70, 140)
    draw.ellipse([sun_x - sun_r, 220 - sun_r, sun_x + sun_r, 220 + sun_r], fill=accent)
    for layer in range(3):
        base = 480 + layer * 130
        points = [(0, size)]
        for x in range(0, size + 90, 90):
            points.append((x, base + rng.randint(-60, 40)))
        points.append((size, size))
        draw.polygon(points, fill=dark if layer == 2 else (accent if layer == 1 else '#9aa5a0'))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=82)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Create fictional demo users, follows, posts, comments, likes and stories.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='Password given to every demo account.')

    def handle(self, *args, password, **options):
        if User.objects.filter(email__endswith='@demo.instacham.test').exists():
            raise CommandError('Demo data already exists.')

        rng = random.Random(7)
        users = []
        for username, nickname, bio in PEOPLE:
            user = User.objects.create_user(
                email=f'{username.split(".")[0]}@demo.instacham.test', username=username, password=password
            )
            user.profile.nickname = nickname
            user.profile.bio = bio
            user.profile.save()
            users.append(user)

        for follower in users:
            for following in users:
                if follower != following:
                    Follow.objects.create(follower=follower, following=following)

        for index, (title, caption) in enumerate(POSTS):
            author = users[index % len(users)]
            post = Post(user=author, title=title, caption=caption)
            post.image.save(f'demo-{index}.jpg', render_scene(index), save=False)
            post.save()
            for fan in rng.sample(users, rng.randint(1, len(users) - 1)):
                if fan != author:
                    Like.objects.create(user=fan, post=post)
            for commenter in rng.sample(users, 2):
                if commenter != author:
                    top = Comment.objects.create(user=commenter, post=post, text=rng.choice(COMMENTS))
                    Comment.objects.create(user=author, post=post, parent=top, text='Thank you!')

        for index, user in enumerate(users[1:], start=1):
            story = Story(user=user, title=f'{user.profile.nickname} today', content='Out and about')
            story.media.save(f'story-{index}.jpg', render_scene(100 + index, size=480), save=False)
            story.save()

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(users)} users, {len(POSTS)} posts and {len(users) - 1} stories. '
            f'Log in as {users[0].email}.'
        ))
