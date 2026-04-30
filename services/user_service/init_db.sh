#! /bin/bash

DB="user_service"

source .env
export PGPASSWORD="$DB_PASSWORD"
echo "$PGPASSWORD"

psql -U asura -d postgres -h localhost -p 5432 -c "DROP DATABASE IF EXISTS $DB WITH (FORCE);"
psql -U asura -d postgres -h localhost -p 5432 -c "CREATE DATABASE $DB;"

source ../../.venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py sample_db

# psql -U asura -d postgres -h localhost -p 5432 -c "SELECT 1;"
# psql -U asura -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE $DB TO asura;"
#
# psql -U asura -d store_service -h localhost -p 5432 -c "SELECT 1;"
