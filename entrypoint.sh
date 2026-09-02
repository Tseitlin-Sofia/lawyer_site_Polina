#!/bin/sh
set -e

echo "→ Применяю миграции"
python manage.py migrate --noinput

if [ "$SKIP_COLLECTSTATIC" != "1" ]; then
  echo "→ Собираю статику"
  python manage.py collectstatic --noinput
fi

exec "$@"
