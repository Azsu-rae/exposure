#! /bin/bash
set -e

DB="social_service"

source .env
export PGPASSWORD="$DB_PASSWORD"

psql -U asura -d postgres -h localhost -p 5432 -c "DROP DATABASE IF EXISTS $DB WITH (FORCE);"
psql -U asura -d postgres -h localhost -p 5432 -c "CREATE DATABASE $DB;"

source ../../.venv/bin/activate

python manage.py makemigrations
python manage.py migrate
