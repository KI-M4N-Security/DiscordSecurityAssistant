#!/bin/bash
# Complete Discord Bot Setup and Launcher

echo "🛡️  Discord Security Bot - Complete Setup"
echo "======================================"
echo ""

# Check dependencies
echo "📋 Checking dependencies..."
python3 -c "import discord" 2>/dev/null || {
    echo "❌ discord.py not installed. Installing..."
    pip install discord.py
}

echo ""
echo "🔧 Setup Required:"
echo "1. Go to: https://discord.com/developers/applications"
echo "2. Select your application/bot"
echo "3. Go to 'Bot' section"
echo "4. Enable these intents:"
echo "   ✓ MESSAGE CONTENT INTENT"
echo "   ✓ SERVER MEMBERS INTENT (optional)"
echo "5. Copy the Bot Token"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running. Starting it..."
    ollama serve &
    sleep 3
fi

# Check Ollama models
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen:0.5b"; then
    echo "⚠️  qwen:0.5b model not found. Pulling it..."
    ollama pull qwen:0.5b
fi

echo ""
echo "🚀 Starting Discord Bot..."
echo "📝 Make sure your bot has these permissions in Discord:"
echo "   ✓ Send Messages"
echo "   ✓ Read Message History"
echo "   ✓ Use External Emojis"
echo ""

# Set environment and start
export MODE=discord
export DISCORD_TOKEN="YOURDISCORDTOKEN"
python3 discord_integration.py
