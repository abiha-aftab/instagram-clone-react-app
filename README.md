# Instagram-style photo app

A take-home project: a small Instagram-like app with a Django REST backend and a React frontend.

## Backend (`check_back/`)

Django + Django REST Framework, JWT auth (SimpleJWT with token blacklist), PostgreSQL, Celery + Redis for background tasks (django-celery-beat).

Apps: `users`, `posts` (posts and comments), `stories`, `notifications`.

```bash
cd check_back
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers celery django-celery-beat psycopg2-binary redis   # no requirements file yet
python manage.py migrate
python manage.py runserver
```

## Frontend (`frontend/`)

React + Vite, React Router, TanStack Query, Axios with JWT handling: login/register, feed, create post, comments.

```bash
cd frontend
npm install
npm run dev
```
