#!/bin/bash
# Discord Bot Launcher

echo "🤖 Discord Security Bot Launcher"
echo "================================"
echo ""
echo "Choose mode:"
echo "1) Discord Bot (connects to Discord app)"
echo "2) MCP Server (for testing via MCP calls)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🚀 Starting Discord Bot..."
        export MODE=discord
        export DISCORD_TOKEN="MTQ3MDQ0OTg4Mzk1MjcwOTcxNA.GELb3A.85d6D4V3UO9b7Wa8yqRuKnFkvLrustjmcnNORg"
        python3 discord_integration.py
        ;;
    2)
        echo "🔧 Starting MCP Server..."
        export MODE=mcp
        python3 discord_integration.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac