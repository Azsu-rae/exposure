#! /bin/bash

# DJANGO_SETTINGS_MODULE="store_service.settings" python main.py

source ../../.venv/bin/activate
python manage.py test_code
