#!/bin/sh
set -e

echo "Check postgres service availability"
python ~/check_service.py --service-name "${DB_HOST}" --ip "${DB_HOST}" --port "${DB_PORT}"

echo "Apply database migrations"
alembic upgrade head

echo "Running app with uvicorn"
uvicorn src.main:app --host 0.0.0.0 --port 8080

exec "$@"
