#!/bin/bash
set -e

echo "Starting AI Router initialization..."

# Wait for PostgreSQL to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    
    # Extract connection details from DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        until pg_isready -h "$DB_HOST" -p "$DB_PORT" 2>/dev/null; do
            echo "PostgreSQL is unavailable - sleeping"
            sleep 2
        done
        echo "PostgreSQL is ready!"
    fi
fi

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Initialize common providers if requested
if [ "$INIT_COMMON_PROVIDERS" = "true" ]; then
    echo "Initializing common AI providers..."
    python scripts/init_common_providers.py
fi

# Start the application
echo "Starting AI Router application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'