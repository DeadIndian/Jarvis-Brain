from datetime import datetime
from typing import Dict, Any
from .base_tool import Tool


class TimeTool(Tool):
    name = "time"
    
    async def execute(self, input_data: Dict[str, Any]) -> str:
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
