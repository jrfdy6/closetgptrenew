#!/bin/bash
# Start script for HTTP gateway that handles Railway's PORT variable

# Railway sets PORT, default to 8080 if not set
PORT=${PORT:-8080}

echo "🚀 Starting HTTP Gateway on port $PORT"
uvicorn mcp_http_gateway:app --host 0.0.0.0 --port $PORT

