from typing import List, Dict, Any
import json


class MemoryStore:
    def __init__(self):
        self.memories: List[Dict[str, Any]] = []
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None):
        memory = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        }
        self.memories.append(memory)
        return memory
    
    def get_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.memories[-limit:]
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Simple keyword search for now
        query_lower = query.lower()
        results = []
        for memory in self.memories:
            if query_lower in memory["content"].lower():
                results.append(memory)
                if len(results) >= limit:
                    break
        return results
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
