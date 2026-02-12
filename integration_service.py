#!/usr/bin/env python3
"""
Clean MCP Integration Service
Connects to existing Discord bots and provides MCP tools
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class CleanMCPServer:
    def __init__(self, config_file: str = "/app/config/personal_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load personal configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "personal": {
                "name": "Security Researcher",
                "team": "Red Team"
            },
            "agent_settings": {
                "default_scan_type": "quick",
                "auto_save_reports": True
            },
            "tool_preferences": {
                "port_scanner": "security",
                "payload_generator": "security"
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
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
        """List available integration tools"""
        return {
            "result": {
                "tools": [
                    {
                        "name": "get_config",
                        "description": "Get personal or agent configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "section": {
                                    "type": "string", 
                                    "description": "Config section: personal, agent_settings, tool_preferences"
                                }
                            }
                        }
                    },
                    {
                        "name": "update_config",
                        "description": "Update configuration values",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "section": {"type": "string", "description": "Config section"},
                                "updates": {"type": "object", "description": "Key-value updates"}
                            },
                            "required": ["section", "updates"]
                        }
                    },
                    {
                        "name": "integration_status",
                        "description": "Check integration status with existing tools",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration tools"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "get_config":
                section = arguments.get("section", "personal")
                config_section = self.config.get(section, {})
                return {
                    "result": {
                        "content": [{
                            "type": "text", 
                            "text": f"Configuration [{section}]:\\n{json.dumps(config_section, indent=2)}"
                        }]
                    }
                }
            
            elif tool_name == "update_config":
                section = arguments["section"]
                updates = arguments["updates"]
                
                if section in self.config:
                    self.config[section].update(updates)
                    # Save config
                    try:
                        with open(self.config_file, 'w') as f:
                            json.dump(self.config, f, indent=2)
                        return {
                            "result": {
                                "content": [{
                                    "type": "text", 
                                    "text": f"Updated [{section}] with: {list(updates.keys())}"
                                }]
                            }
                        }
                    except Exception as e:
                        return {"error": {"code": -32603, "message": f"Save failed: {str(e)}"}}
                else:
                    return {"error": {"code": -32602, "message": f"Section {section} not found"}}
            
            elif tool_name == "integration_status":
                status_info = []
                
                # Check Docker containers
                try:
                    import subprocess
                    result = subprocess.run(['docker', 'ps', '--format', 'json'], 
                                      capture_output=True, text=True)
                    if result.returncode == 0:
                        containers = json.loads(result.stdout)
                        security_containers = [c for c in containers if 'security' in c.get('Names', [''])[0].lower()]
                        status_info.append(f"Security containers: {len(security_containers)}")
                        for container in security_containers:
                            name = container.get('Names', [''])[0]
                            state = container.get('State', 'unknown')
                            status_info.append(f"  - {name}: {state}")
                    else:
                        status_info.append("Docker status check failed")
                except:
                    status_info.append("Docker integration: Not available")
                
                # Check config files
                config_files = ['targets.json', 'personal_config.json']
                for config_file in config_files:
                    if os.path.exists(f"/app/config/{config_file}"):
                        status_info.append(f"Config available: {config_file}")
                
                return {
                    "result": {
                        "content": [{
                            "type": "text", 
                            "text": "Integration Status:\\n" + "\\n".join(status_info)
                        }]
                    }
                }
            
            else:
                return {"error": {"code": -32602, "message": f"Tool '{tool_name}' not found"}}
                
        except Exception as e:
            return {"error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}}

    async def run_stdio_server(self):
        """Run MCP server using stdio"""
        print("Clean MCP Integration Server started", file=sys.stderr)
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
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
    server = CleanMCPServer()
    asyncio.run(server.run_stdio_server())