from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class RemoteRequest(BaseModel):
    input: str
    memory_context: List[Dict[str, Any]] = []
    client_state: Optional[Dict[str, Any]] = {}


class RemoteResponse(BaseModel):
    text: str
    actions: List[Dict[str, Any]] = []
    meta: Dict[str, Any] = {}
