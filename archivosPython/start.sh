#!/bin/sh
# Arranque en la nube (Render): migraciones, estáticos, admin inicial y Gunicorn.
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py crear_admin
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
