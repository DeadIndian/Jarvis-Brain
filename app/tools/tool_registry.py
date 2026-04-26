from typing import Dict, Type
from .base_tool import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]
    
    def list_tools(self) -> Dict[str, Tool]:
        return self._tools.copy()


# Global registry instance
tool_registry = ToolRegistry()
