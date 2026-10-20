#!/bin/sh
set -e

if [ "$1" = "gunicorn" ]; then
    echo "→ Миграции"
    python manage.py migrate --noinput
    echo "→ Демо-данные"
    python manage.py seed_demo

    if [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
        python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username='admin')
u.set_password(os.environ['DJANGO_ADMIN_PASSWORD'])
u.save()"
    fi

    export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
    rm -rf "$PROMETHEUS_MULTIPROC_DIR"
    mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
fi

exec "$@"