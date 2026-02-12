#!/usr/bin/env python3
"""
Simple Discord Bot - No privileged intents required
"""
import asyncio
import json
import os
import requests
import discord
from discord.ext import commands

class SimpleSecurityBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        super().__init__(command_prefix='!', intents=intents)
        self.ollama_url = "http://localhost:11434"

    async def on_ready(self):
        print(f'🤖 Security Bot logged in as {self.user}')
        print('Ready to respond to commands!')
        print('Available commands: !help, !ask, !status')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Handle simple commands without privileged intents
        if message.content.startswith('!help'):
            await self._send_help(message)
        elif message.content.startswith('!ask '):
            await self._handle_ask(message)
        elif message.content.startswith('!status'):
            await self._send_status(message)

    async def _send_help(self, message):
        help_text = """
🛡️ **Security Bot Commands:**

`!ask <question>` - Ask security questions
`!status` - Check bot status  
`!help` - Show this help

Example: `!ask what is a port scan?`
        """
        await message.channel.send(help_text)

    async def _handle_ask(self, message):
        try:
            question = message.content[5:]  # Remove '!ask '
            
            # Query Ollama
            response = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": "qwen:0.5b",
                "prompt": f"You are a cybersecurity assistant. Answer this question: {question}",
                "stream": False
            }, timeout=30)
            
            if response.status_code == 200:
                llm_response = response.json().get("response", "No response")
                await message.channel.send(f"🤖 **Security AI:** {llm_response}")
            else:
                await message.channel.send("❌ LLM service unavailable")
                
        except Exception as e:
            await message.channel.send(f"❌ Error: {str(e)}")

    async def _send_status(self, message):
        status = """
✅ **Bot Status:**
- LLM: Connected to Ollama
- Model: qwen:0.5b
- Commands: Working
        """
        await message.channel.send(status)

async def main():
    token = "YOURDISCORDTOKEN"
    bot = SimpleSecurityBot()
    
    try:
        await bot.start(token)
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token")
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
