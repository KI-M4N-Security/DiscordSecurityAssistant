#!/bin/bash
# Discord Bot Launcher

echo "🤖 Discord Security Bot Launcher"
echo "================================"
echo ""
echo "📋 Pre-flight checks..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running. Starting it..."
    ollama serve &
    sleep 3
fi

# Check Ollama models
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen:0.5b"; then
    echo "⚠️  qwen:0.5b model not found. Please run: ollama pull qwen:0.5b"
fi

echo ""
echo "🚀 Starting Discord Bot..."
export MODE=discord
export DISCORD_TOKEN="MTQ3MDQ0OTg4Mzk1MjcwOTcxNA.GELb3A.85d6D4V3UO9b7Wa8yqRuKnFkvLrustjmcnNORg"
python3 discord_integration.py