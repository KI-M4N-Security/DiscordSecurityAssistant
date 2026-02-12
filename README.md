# Security Discord Bot
A Discord bot with AI-powered security assistance using Ollama and MCP (Model Context Protocol).

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Ollama installed and running
- Discord bot token

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd security-discord-bot

# Install dependencies
pip install -r requirements.txt

# Pull Ollama model
ollama pull qwen:0.5b  # or llama3.2 for better performance
```

### Configuration
1. **Set Discord Token:**
   ```bash
   export DISCORD_TOKEN="your_bot_token_here"
   ```

2. **Optional: Change Ollama Model:**
   - Edit `simple_discord_bot.py` line 88
   - Change `"qwen:0.5b"` to `"llama3.2"` or any available model

### Running the Bot

#### Option 1: Simple Bot (Recommended for quick start)
```bash
python3 simple_discord_bot.py
```

#### Option 2: Full MCP Bot
```bash
export MODE=discord
python3 discord_integration.py
```

#### Option 3: Using Launcher Scripts
```bash
# For simple bot
./simple_bot.sh

# For full setup with checks
./setup_discord_bot.sh
```

## 🛡️ Discord Setup

### Enable Privileged Intents (Required for full functionality)
1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to "Bot" section
4. Enable:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (optional)
5. Save and copy bot token

### Bot Permissions
Add your bot to servers with these permissions:
- Send Messages
- Read Message History
- Use External Emojis

## 📋 Available Commands

- `!help` - Show all available commands
- `!ask <question>` - Ask AI security questions
- `!status` - Check bot and service status
- `!target <domain>` - Set target for operations (full bot)
- `!scan <type>` - Run security scans (full bot)

## 🔧 Configuration Files

### Environment Variables
- `DISCORD_TOKEN` - Your Discord bot token
- `MODE` - "discord" for Discord mode, "mcp" for testing
- `OLLAMA_MODEL` - Ollama model to use (default: qwen:0.5b)

### Key Files
- `simple_discord_bot.py` - Basic Discord bot (no privileged intents)
- `discord_integration.py` - Full MCP-enabled bot
- `requirements.txt` - Python dependencies
- `setup_discord_bot.sh` - Full setup script with checks
- `simple_bot.sh` - Simple bot launcher

## 🧪 Testing

### Test without Discord
```bash
# Test MCP functionality
echo '{"method": "tools/call", "params": {"name": "ask_llm", "arguments": {"question": "What is a port scan?"}}}' | python3 discord_integration.py
```

### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```

## 📝 Bot Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Discord App   │───▶│  Discord Bot    │───▶│   Ollama LLM   │
│   (!commands)  │    │  (Processing)   │    │  (AI Service)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  MCP Services   │
                       │ (optional)      │
                       └──────────────────┘
```

## 🔍 Model Recommendations

- **qwen:0.5b** - Fast, low memory (good for VMs)
- **llama3.2** - Better responses, more memory needed
- **codellama** - Code-focused assistance

Change model in bot files:
```python
"model": "your_chosen_model"
```

## 🚀 Deployment on New Machine

1. **Clone:**
   ```bash
   git clone <your-repo-url>
   cd security-discord-bot
   ```

2. **Setup:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment
   export DISCORD_TOKEN="new_bot_token"
   export OLLAMA_MODEL="llama3.2"  # For better performance
   
   # Pull preferred model
   ollama pull $OLLAMA_MODEL
   ```

3. **Run:**
   ```bash
   python3 simple_discord_bot.py
   ```

## 🐛 Troubleshooting

### Bot not responding
- Check Discord token is valid
- Verify privileged intents are enabled
- Check bot has server permissions

### Ollama connection issues
```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Permission denied commands
- Check `simple_discord_bot.py` vs `discord_integration.py`
- Full bot requires privileged intents

## 📄 License

This is a security research tool. Use responsibly and only on targets you have permission to test.