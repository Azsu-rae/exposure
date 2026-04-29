#!/bin/sh

python manage.py migrate --noinput
exec gunicorn user_service.wsgi:application --bind 0.0.0.0:8000 --workers 3
