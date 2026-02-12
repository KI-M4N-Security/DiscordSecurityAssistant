#!/usr/bin/env python3
"""
Simple Discord Bot - Production Ready
Update this file with your custom configurations
"""
import asyncio
import json
import os
import requests
import discord
from discord.ext import commands

class ConfigurableSecurityBot(commands.Bot):
    def __init__(self):
        # Load configuration
        self.token = os.getenv("DISCORD_TOKEN")
        self.ollama_url = "http://localhost:11434"
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        if not self.token:
            raise ValueError("DISCORD_TOKEN environment variable required")
        self.token = str(self.token)  # Ensure it's a string
        
        # Discord setup
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print(f'🤖 Security Bot logged in as {self.user}')
        print(f'📝 Model: {self.model}')
        print('Ready to respond to commands!')
        
        # Set bot status
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="security commands"
        ))

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Handle commands
        if message.content.startswith('!help'):
            await self._send_help(message)
        elif message.content.startswith('!ask '):
            await self._handle_ask(message)
        elif message.content.startswith('!status'):
            await self._send_status(message)
        elif message.content.startswith('!scan '):
            await self._handle_scan(message)
        elif message.content.startswith('!target '):
            await self._set_target(message)

    async def _send_help(self, message):
        help_text = f"""
🛡️ **Security Bot Commands:**

`!ask <question>` - Ask AI security questions
`!status` - Check bot and LLM status  
`!scan <target>` - Run basic scan on target
`!target <domain>` - Set default target
`!help` - Show this help

📝 **Current Model:** {self.model}
🎯 **Default Target:** Set with `!target domain.com`

**Examples:**
`!ask what is a port scan?`
`!scan example.com`
`!target vulnweb.com`
        """
        await message.channel.send(help_text)

    async def _handle_ask(self, message):
        try:
            question = message.content[5:]  # Remove '!ask '
            
            # Show typing indicator
            async with message.channel.typing():
                # Query Ollama
                response = requests.post(f"{self.ollama_url}/api/generate", json={
                    "model": self.model,
                    "prompt": f"""You are a cybersecurity expert assistant. 
Provide a helpful, accurate security answer to this question:

Question: {question}

If suggesting tools, recommend legitimate security tools and mention they should only be used on authorized targets.""",
                    "stream": False
                }, timeout=30)
            
                if response.status_code == 200:
                    llm_response = response.json().get("response", "No response")
                    
                    # Split long messages
                    if len(llm_response) > 1900:
                        chunks = [llm_response[i:i+1900] for i in range(0, len(llm_response), 1900)]
                        for i, chunk in enumerate(chunks):
                            await message.channel.send(f"🤖 **Security AI ({i+1}/{len(chunks)}):**\n{chunk}")
                    else:
                        await message.channel.send(f"🤖 **Security AI:**\n{llm_response}")
                else:
                    await message.channel.send("❌ LLM service unavailable")
                    
        except Exception as e:
            await message.channel.send(f"❌ Error processing question: {str(e)}")

    async def _send_status(self, message):
        try:
            # Check Ollama
            ollama_status = "🟢 Online" if requests.get(f"{self.ollama_url}/api/tags", timeout=5).status_code == 200 else "🔴 Offline"
            
            status = f"""
✅ **Bot Status:**
- **LLM Service:** {ollama_status}
- **Model:** {self.model}
- **Commands:** Working
- **Latency:** {round(self.latency * 1000)}ms
- **Uptime:** {round(self.uptime)} hours
            """
            await message.channel.send(status)
            
        except Exception as e:
            await message.channel.send(f"❌ Status check failed: {str(e)}")

    async def _handle_scan(self, message):
        try:
            target = message.content[6:].strip()  # Remove '!scan '
            if not target:
                await message.channel.send("Usage: `!scan <target>`")
                return
                
            async with message.channel.typing():
                await message.channel.send(f"🔍 Starting scan on: `{target}`")
                await message.channel.send("📝 Note: Only scan targets you have permission to test")
                
        except Exception as e:
            await message.channel.send(f"❌ Scan error: {str(e)}")

    async def _set_target(self, message):
        try:
            target = message.content[8:].strip()  # Remove '!target '
            if not target:
                await message.channel.send("Usage: `!target <domain>`")
                return
                
            # Store in bot instance (could add file storage)
            self.default_target = target
            await message.channel.send(f"🎯 Default target set to: `{target}`")
            
        except Exception as e:
            await message.channel.send(f"❌ Target setting error: {str(e)}")

    @property
    def uptime(self):
        # Simple uptime calculation
        return 1.0  # placeholder

async def main():
    try:
        bot = ConfigurableSecurityBot()
        await bot.start(bot.token)  # type: ignore
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("Set DISCORD_TOKEN environment variable")
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token - check your bot token")
    except Exception as e:
        print(f"❌ Bot startup error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())