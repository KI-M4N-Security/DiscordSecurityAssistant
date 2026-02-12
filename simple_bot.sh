#!/bin/bash
# Simple Bot Launcher

echo "🤖 Simple Security Discord Bot Launcher"
echo "===================================="
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running. Starting it..."
    ollama serve &
    sleep 3
fi

# Check Ollama model
MODEL=${OLLAMA_MODEL:-"qwen:0.5b"}
if ! curl -s http://localhost:11434/api/tags | grep -q "$MODEL"; then
    echo "⚠️  Model $MODEL not found. Pulling it..."
    ollama pull $MODEL
fi

echo "🚀 Starting Simple Discord Bot..."
echo "📝 Model: $MODEL"
echo "📝 Discord Token: ${DISCORD_TOKEN:0:10}..."
echo ""

# Set environment and start
export OLLAMA_MODEL=$MODEL
python3 simple_discord_bot.py