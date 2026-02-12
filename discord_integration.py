#!/usr/bin/env python3
"""
Discord-LLM-MCP Integration Service
Connects Discord bot to Ollama LLM and MCP security tools
"""

import asyncio
import json
import sys
import os
import subprocess
import requests
from typing import Dict, List, Any, Optional
import discord
from discord.ext import commands

class DiscordLLMIntegration:
    def __init__(self):
        self.discord_token = os.getenv("YOUR DISCORD TOKEN")
        self.ollama_url = "http://localhost:11434"
        self.mcp_servers = {
            "general": "mcp-general-tools",
            "security": "mcp-security-tools", 
            "target": "target-config-service",
            "recon": "passive-recon-tools",
            "web": "web-security-tools",
            "password": "password-analysis-tools"
        }
        self.current_target = None
        self.permissions = {}  # User permissions for tools
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests from Discord integration"""
        try:
            if request.get("method") == "tools/list":
                return self._list_tools()
            elif request.get("method") == "tools/call":
                return await self._call_tool(request.get("params", {}))
            else:
                return {"error": {"code": -32601, "message": "Method not found"}}
        except Exception as e:
            return {"error": {"code": -32603, "message": str(e)}}
    
    def _list_tools(self) -> Dict[str, Any]:
        """List Discord integration tools"""
        return {
            "result": {
                "tools": [
                    {
                        "name": "discord_command",
                        "description": "Process Discord command and route to LLM/tools",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "Discord user ID"},
                                "command": {"type": "string", "description": "Discord command"},
                                "args": {"type": "array", "description": "Command arguments", "items": {"type": "string"}},
                                "channel_id": {"type": "string", "description": "Discord channel ID"}
                            },
                            "required": ["user_id", "command", "args", "channel_id"]
                        }
                    },
                    {
                        "name": "ask_llm",
                        "description": "Query Ollama LLM for security assistance",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string", "description": "Security question"},
                                "context": {"type": "string", "description": "Additional context"}
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "set_target",
                        "description": "Set current target for operations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "target": {"type": "string", "description": "Target domain/IP"}
                            },
                            "required": ["target"]
                        }
                    },
                    {
                        "name": "get_status",
                        "description": "Get current system status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord integration tools"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "discord_command":
                return await self._discord_command(arguments)
            elif tool_name == "ask_llm":
                return await self._ask_llm(arguments)
            elif tool_name == "set_target":
                return await self._set_target(arguments)
            elif tool_name == "get_status":
                return await self._get_status(arguments)
            else:
                return {"error": {"code": -32602, "message": f"Tool '{tool_name}' not found"}}
        except Exception as e:
            return {"error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}}
    
    async def _discord_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process Discord commands and route appropriately"""
        user_id = args["user_id"]
        command = args["command"]
        cmd_args = args.get("args", [])
        channel_id = args.get("channel_id", "")
        
        # Check user permissions
        if not self._check_permission(user_id, command):
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": "❌ You don't have permission to use this command"
                    }]
                }
            }
        
        # Route commands
        if command == "!scan":
            return await self._handle_scan(cmd_args)
        elif command == "!target":
            return await self._handle_target(cmd_args)
        elif command == "!ask":
            return await self._handle_ask(cmd_args)
        elif command == "!status":
            return await self._handle_status()
        elif command == "!tools":
            return await self._handle_tools()
        elif command == "!help":
            return await self._handle_help()
        else:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown command: {command}\\nUse !help for available commands"
                    }]
                }
            }
    
    async def _handle_scan(self, args: List[str]) -> Dict[str, Any]:
        """Handle scan commands"""
        if not self.current_target:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": "❌ No target set. Use `!target example.com` first"
                    }]
                }
            }
        
        scan_type = args[0] if args else "quick"
        
        if scan_type == "quick":
            # Quick port scan
            result = await self._call_mcp_tool("security", "port_scan", {
                "target": self.current_target,
                "ports": "22,80,443,8080"
            })
        elif scan_type == "recon":
            # Passive reconnaissance
            result = await self._call_mcp_tool("recon", "subdomain_harvest", {
                "domain": self.current_target
            })
        elif scan_type == "web":
            # Web security scan
            result = await self._call_mcp_tool("web", "web_scan", {
                "target": f"http://{self.current_target}",
                "tools": ["nikto"]
            })
        else:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": "Available scan types: quick, recon, web"
                    }]
                }
            }
        
        return result
    
    async def _handle_target(self, args: List[str]) -> Dict[str, Any]:
        """Handle target setting"""
        if not args:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": "Usage: `!target example.com`"
                    }]
                }
            }
        
        target = args[0]
        self.current_target = target
        
        # Also update target config service
        await self._call_mcp_tool("target", "set_target", {
            "target_name": target
        })
        
        return {
            "result": {
                "content": [{
                    "type": "text",
                    "text": f"🎯 Target set to: {target}"
                }]
            }
        }
    
    async def _handle_ask(self, args: List[str]) -> Dict[str, Any]:
        """Handle LLM questions"""
        if not args:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": "Usage: `!ask your security question here`"
                    }]
                }
            }
        
        question = " ".join(args)
        return await self._ask_llm({"question": question})
    
    async def _handle_status(self) -> Dict[str, Any]:
        """Handle status requests"""
        status_info = []
        
        # Check current target
        if self.current_target:
            status_info.append(f"🎯 Current Target: {self.current_target}")
        else:
            status_info.append("🎯 Current Target: Not set")
        
        # Check MCP servers
        for name, container in self.mcp_servers.items():
            try:
                result = subprocess.run(['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Status}}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    status_info.append(f"✅ {name}: {result.stdout.strip()}")
                else:
                    status_info.append(f"❌ {name}: Not running")
            except:
                status_info.append(f"❓ {name}: Unknown status")
        
        return {
            "result": {
                "content": [{
                    "type": "text",
                    "text": "🛡️ Security Agent Status:\\n" + "\\n".join(status_info)
                }]
            }
        }
    
    async def _handle_tools(self) -> Dict[str, Any]:
        """List available tools"""
        tools_info = [
            "🛡️ Available Security Tools:",
            "🔍 **Scanning**: !scan quick/recon/web",
            "🎯 **Target**: !target domain.com", 
            "🤖 **AI Assistant**: !ask your question",
            "📊 **Status**: !status",
            "❓ **Help**: !help"
        ]
        
        return {
            "result": {
                "content": [{
                    "type": "text",
                    "text": "\\n".join(tools_info)
                }]
            }
        }
    
    async def _handle_help(self) -> Dict[str, Any]:
        """Show help information"""
        help_text = """
🛡️ **Daily Security Agent - Discord Commands**

🎯 **Target Management**
`!target example.com` - Set active target
`!status` - Check current status

🔍 **Security Scanning** 
`!scan quick` - Quick port scan
`!scan recon` - Passive reconnaissance
`!scan web` - Web security scan

🤖 **AI Assistant**
`!ask what is a good port scanning technique?` - Ask security questions

📊 **Information**
`!tools` - List available tools
`!help` - Show this help message

**Workflow**: 1. Set target → 2. Choose scan → 3. Ask AI for analysis
        """
        
        return {
            "result": {
                "content": [{
                    "type": "text",
                    "text": help_text
                }]
            }
        }
    
    async def _ask_llm(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query Ollama LLM"""
        question = args["question"]
        context = args.get("context", "")
        
        try:
            # Prepare prompt with security context
            prompt = f"""You are a cybersecurity assistant. Answer this security question:

Question: {question}

Context: {context if context else 'General security inquiry'}

Current target: {self.current_target if self.current_target else 'None set'}

Provide a helpful, accurate security answer. If you need to suggest tools, mention the available scan commands."""
            
            # Query Ollama
            response = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": "qwen:0.5b",
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            
            if response.status_code == 200:
                llm_response = response.json().get("response", "No response")
                return {
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"🤖 **Security AI Response:**\\n{llm_response}"
                        }]
                    }
                }
            else:
                return {
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": "❌ LLM service unavailable"
                        }]
                    }
                }
        except Exception as e:
            return {
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"❌ LLM query failed: {str(e)}"
                    }]
                }
            }
    
    async def _set_target(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set current target"""
        target = args["target"]
        self.current_target = target
        
        return {
            "result": {
                "content": [{
                    "type": "text",
                    "text": f"🎯 Target set to: {target}"
                }]
            }
        }
    
    async def _get_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get system status"""
        return await self._handle_status()
    
    async def _call_mcp_tool(self, server: str, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool in Docker container"""
        try:
            container_name = self.mcp_servers[server]
            
            # Prepare MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool,
                    "arguments": arguments
                }
            }
            
            # Execute in container
            cmd = [
                "docker", "exec", container_name,
                "echo", json.dumps(mcp_request),
                "|", "python3", "-c", 
                "import json, sys; print(json.dumps(json.load(sys.stdin)))"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"❌ Tool execution failed: {result.stderr}"
                        }]
                    }
                }
        except Exception as e:
            return {
                "error": {"code": -32603, "message": f"MCP tool call failed: {str(e)}"}
            }
    
    def _check_permission(self, user_id: str, command: str) -> bool:
        """Check user permissions for commands"""
        # Simple permission system - can be expanded
        # For now, allow all basic commands
        allowed_commands = ["!help", "!status", "!tools", "!ask", "!target", "!scan"]
        return True  # Allow all commands for testing - can add user restrictions later

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Try without privileged intents first
        intents.guilds = True
        intents.messages = True
        try:
            intents.message_content = True
        except:
            print("⚠️  message_content intent not enabled - bot may not see all messages")
        super().__init__(command_prefix='!', intents=intents)
        self.integration = DiscordLLMIntegration()

    async def on_ready(self):
        print(f'🤖 Bot logged in as {self.user}')
        if self.user:
            print(f'Bot ID: {self.user.id}')
        print('Ready to respond to commands!')

    async def on_message(self, message):
        # Don't respond to own messages
        if message.author == self.user:
            return

        # Handle commands
        if message.content.startswith('!'):
            await self.process_message(message)
        
        # Let commands framework handle other commands
        await self.process_commands(message)

    async def process_message(self, message):
        """Process Discord messages using the integration"""
        try:
            # Extract command and args
            parts = message.content.split()
            command = parts[0] if parts else ""
            args = parts[1:] if len(parts) > 1 else []
            
            # Convert to MCP format
            result = await self.integration.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "discord_command",
                    "arguments": {
                        "user_id": str(message.author.id),
                        "command": command,
                        "args": args,
                        "channel_id": str(message.channel.id)
                    }
                }
            })
            
            # Send response back to Discord
            if "result" in result and "content" in result["result"]:
                for content_item in result["result"]["content"]:
                    if content_item.get("type") == "text":
                        # Split long messages to Discord's 2000 char limit
                        text = content_item["text"]
                        for chunk in [text[i:i+1990] for i in range(0, len(text), 1990)]:
                            await message.channel.send(chunk)
            elif "error" in result:
                await message.channel.send(f"❌ Error: {result['error'].get('message', 'Unknown error')}")
                
        except Exception as e:
            await message.channel.send(f"❌ Bot error: {str(e)}")

async def run_discord_bot():
    """Run Discord bot"""
    bot = DiscordBot()
    token = os.getenv("DISCORD_TOKEN") or "MTQ3MDQ0OTg4Mzk1MjcwOTcxNA.GELb3A.85d6D4V3UO9b7Wa8yqRuKnFkvLrustjmcnNORg"
    
    if not token:
        print("❌ Discord token not found in environment variables")
        print("Set the DISCORD_TOKEN environment variable")
        return
    
    try:
        await bot.start(token)
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token - check your bot token")
    except Exception as e:
        print(f"❌ Bot startup error: {str(e)}")

async def run_stdio_server():
    """Run MCP server on stdio"""
    server = DiscordLLMIntegration()
    print("Discord-LLM-MCP Integration Server started on stdio", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({"error": {"code": -32603, "message": str(e)}}))
            sys.stdout.flush()

if __name__ == "__main__":
    mode = os.getenv("MODE", "mcp")  # Default to MCP mode
    
    if mode == "discord":
        print("🚀 Starting Discord Bot...")
        asyncio.run(run_discord_bot())
    else:
        print("🔧 Starting MCP Server...")
        asyncio.run(run_stdio_server())
