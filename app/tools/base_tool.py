from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    name: str = ""
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> str:
        pass
