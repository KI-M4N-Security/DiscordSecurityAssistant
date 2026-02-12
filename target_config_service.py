#!/usr/bin/env python3
"""
Target Configuration Service
Central place to manage targets, ports, and configurations
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class TargetManager:
    def __init__(self, config_file: str = "/app/config/targets.json"):
        self.config_file = config_file
        self.targets = self._load_targets()
        
    def _load_targets(self) -> Dict[str, Any]:
        """Load targets from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            print(f"Error loading targets: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default target configuration"""
        return {
            "current_target": "example.com",
            "targets": {
                "example.com": {
                    "ip": "93.184.216.34",
                    "ports": "22,80,443,8080",
                    "description": "Example target for testing",
                    "type": "web_server",
                    "tags": ["test", "demo"],
                    "created": datetime.now().isoformat()
                },
                "local_test": {
                    "ip": "192.168.1.1",
                    "ports": "22,80,443,53",
                    "description": "Local router/test target",
                    "type": "network_device",
                    "tags": ["local", "test"],
                    "created": datetime.now().isoformat()
                }
            },
            "global_settings": {
                "default_ports": "22,80,443,8080,3000,8000,9000",
                "timeout": 5,
                "scan_threads": 50,
                "output_format": "json"
            }
        }
    
    def save_targets(self) -> bool:
        """Save targets to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.targets, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving targets: {e}")
            return False
    
    def set_current_target(self, target_name: str) -> bool:
        """Set the current active target"""
        if target_name in self.targets["targets"]:
            self.targets["current_target"] = target_name
            return self.save_targets()
        return False
    
    def get_current_target(self) -> Optional[Dict[str, Any]]:
        """Get current target configuration"""
        current = self.targets.get("current_target")
        if current and current in self.targets["targets"]:
            return self.targets["targets"][current]
        return None
    
    def add_target(self, name: str, config: Dict[str, Any]) -> bool:
        """Add new target"""
        self.targets["targets"][name] = {
            **config,
            "created": datetime.now().isoformat()
        }
        return self.save_targets()
    
    def list_targets(self) -> List[Dict[str, Any]]:
        """List all targets"""
        targets_list = []
        for name, config in self.targets["targets"].items():
            targets_list.append({
                "name": name,
                **config,
                "is_current": name == self.targets.get("current_target")
            })
        return targets_list
    
    def delete_target(self, name: str) -> bool:
        """Delete a target"""
        if name in self.targets["targets"]:
            del self.targets["targets"][name]
            # If this was current target, reset it
            if self.targets.get("current_target") == name:
                self.targets["current_target"] = list(self.targets["targets"].keys())[0] if self.targets["targets"] else None
            return self.save_targets()
        return False
    
    def update_target(self, name: str, updates: Dict[str, Any]) -> bool:
        """Update target configuration"""
        if name in self.targets["targets"]:
            self.targets["targets"][name].update(updates)
            self.targets["targets"][name]["updated"] = datetime.now().isoformat()
            return self.save_targets()
        return False
    
    def get_global_settings(self) -> Dict[str, Any]:
        """Get global settings"""
        return self.targets.get("global_settings", {})
    
    def update_global_settings(self, settings: Dict[str, Any]) -> bool:
        """Update global settings"""
        self.targets["global_settings"].update(settings)
        return self.save_targets()

# For MCP integration
class TargetConfigMCP:
    def __init__(self):
        self.manager = TargetManager()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests for target management"""
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
        """List target management tools"""
        return {
            "result": {
                "tools": [
                    {
                        "name": "set_target",
                        "description": "Set current target for operations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "target_name": {
                                    "type": "string",
                                    "description": "Target name from configuration"
                                }
                            },
                            "required": ["target_name"]
                        }
                    },
                    {
                        "name": "get_current_target",
                        "description": "Get current target configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "list_targets",
                        "description": "List all configured targets",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "add_target",
                        "description": "Add new target configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Target name"},
                                "ip": {"type": "string", "description": "Target IP address"},
                                "ports": {"type": "string", "description": "Ports to scan"},
                                "description": {"type": "string", "description": "Target description"},
                                "type": {"type": "string", "description": "Target type"}
                            },
                            "required": ["name", "ip"]
                        }
                    }
                ]
            }
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute target management tools"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "set_target":
                success = self.manager.set_current_target(arguments["target_name"])
                return {"result": {"content": [{"type": "text", "text": f"Target set to: {arguments['target_name']}"}]}}
            
            elif tool_name == "get_current_target":
                target = self.manager.get_current_target()
                if target:
                    return {"result": {"content": [{"type": "text", "text": f"Current target: {target['name']} ({target['ip']}) - {target.get('description', 'No description')}"}]}}
                else:
                    return {"result": {"content": [{"type": "text", "text": "No current target set"}]}}
            
            elif tool_name == "list_targets":
                targets = self.manager.list_targets()
                output = "Configured targets:\n"
                for target in targets:
                    marker = "🎯" if target["is_current"] else "  "
                    output += f"{marker} {target['name']}: {target['ip']}:{target.get('ports', 'N/A')} - {target.get('description', 'No description')}\n"
                return {"result": {"content": [{"type": "text", "text": output}]}}
            
            elif tool_name == "add_target":
                name = arguments["name"]
                config = {k: v for k, v in arguments.items() if k != "name"}
                success = self.manager.add_target(name, config)
                if success:
                    return {"result": {"content": [{"type": "text", "text": f"Target '{name}' added successfully"}]}}
                else:
                    return {"error": {"code": -32603, "message": "Failed to add target"}}
            
            else:
                return {"error": {"code": -32602, "message": f"Tool '{tool_name}' not found"}}
                
        except Exception as e:
            return {"error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}}

if __name__ == "__main__":
    import asyncio
    import sys
    import json
    
    server = TargetConfigMCP()
    
    async def run_stdio_server():
        print("Target Config MCP Server started on stdio", file=sys.stderr)
        
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
    
    asyncio.run(run_stdio_server())