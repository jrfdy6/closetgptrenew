#!/bin/bash
# Startup script for MCP server on Railway

echo "🚀 Installing MCP dependencies..."
pip install mcp httpx --quiet

echo "✅ Starting MCP server..."
python mcp_server.py

