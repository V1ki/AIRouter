#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

echo "Initializing database..."
python scripts/init_db.py

if [ "$INIT_COMMON_PROVIDERS" = "true" ]; then
    echo "Initializing common providers..."
    python scripts/init_common_providers.py
    
    # Fix prices if they were incorrectly multiplied
    echo "Checking and fixing model prices..."
    python scripts/fix_model_prices.py
fi

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000