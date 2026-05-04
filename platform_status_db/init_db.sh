#! /bin/bash

python -m platform_status_db.manage makemigrations
python -m platform_status_db.manage migrate

# Create a superuser if it doesn't exist
DJANGO_SUPERUSER_PASSWORD=platform_status python -m platform_status_db.manage createsuperuser --username platform_status --email admin@localhost --noinput
