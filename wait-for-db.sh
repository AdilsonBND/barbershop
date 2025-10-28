#!/bin/bash
set -e

echo "Waiting for database to be ready..."

# Wait for database to be ready
until nc -z db 5432; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - continuing..."

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start server
python manage.py runserver 0.0.0.0:8000

