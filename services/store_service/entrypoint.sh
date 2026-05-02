#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$RUN_CONSUMER" = "1" ]; then
    exec python manage.py consume_events
else
    exec gunicorn store_service.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
