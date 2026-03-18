#!/bin/bash
set -e

cd /app/server

echo "Checking for existing migrations..."
MIGRATION_COUNT=$(ls -1 alembic/versions/*.py 2>/dev/null | wc -l)

if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo "No migrations found. Generating initial migration..."
    python -m alembic revision --autogenerate -m "Initial migration"
else
    echo "Migrations already exist. Skipping generation."
fi

echo "Applying migrations..."
python -m alembic upgrade head

echo "Database initialization complete!"
