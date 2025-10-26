#!/bin/bash

# Test ClosetGPT MCP Server locally
# Uses MCP Inspector for interactive testing

echo "🧪 ClosetGPT MCP Server - Local Test"
echo "===================================="
echo ""

# Check if MCP is installed
if ! python -c "import mcp" 2>/dev/null; then
    echo "❌ MCP SDK not installed!"
    echo ""
    echo "Install with:"
    echo "  pip install mcp"
    echo ""
    exit 1
fi

echo "✅ MCP SDK found"
echo ""

# Check for npx (for MCP Inspector)
if ! command -v npx &> /dev/null; then
    echo "⚠️  npx not found - MCP Inspector requires Node.js"
    echo "   Install from: https://nodejs.org"
    echo ""
    echo "Running basic test instead..."
    echo ""
    
    cd backend
    export MAIN_API_URL=https://closetgptrenew-production.railway.app
    export API_KEY=test-key
    
    echo "Starting MCP server..."
    python mcp_server.py &
    PID=$!
    
    sleep 2
    
    echo "Server started (PID: $PID)"
    echo "Press Enter to stop..."
    read
    
    kill $PID 2>/dev/null
    echo "Server stopped"
    exit 0
fi

echo "✅ npx found"
echo ""
echo "🚀 Starting MCP Inspector..."
echo ""
echo "This will open a web UI for testing your MCP tools."
echo "You can:"
echo "  • See all available tools"
echo "  • Test tool calls interactively"
echo "  • Inspect responses and UI components"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd backend

export MAIN_API_URL=https://closetgptrenew-production.railway.app
export API_KEY=test-key

npx @modelcontextprotocol/inspector python mcp_server.py

