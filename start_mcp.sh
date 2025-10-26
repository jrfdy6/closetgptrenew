#!/bin/bash
# Startup script for MCP server on Railway (root level)

echo "🚀 Installing MCP dependencies..."
pip install mcp httpx pydantic python-dotenv --quiet

echo "✅ Starting MCP server..."
python mcp_server.py
