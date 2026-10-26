FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SQLITE_PATH=/data/db.sqlite3 \
    MEDIA_ROOT=/data/media \
    STATIC_ROOT=/app/staticfiles

WORKDIR /app
RUN useradd --create-home --uid 10001 app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app . .
RUN mkdir -p /data/media /app/staticfiles && chown -R app:app /data /app/staticfiles

USER app
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput -v0 && exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -"]
