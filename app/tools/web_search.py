from typing import Dict, Any
from .base_tool import Tool


class WebSearchTool(Tool):
    name = "web_search"
    
    async def execute(self, input_data: Dict[str, Any]) -> str:
        return "Web search not implemented yet"
