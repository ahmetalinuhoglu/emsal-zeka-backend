#!/bin/bash
# Railway startup script

# Default port if PORT env var not set
PORT=${PORT:-8000}

echo "Starting server on port $PORT"
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT 