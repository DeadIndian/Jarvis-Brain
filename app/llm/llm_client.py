from typing import Optional
import asyncio
from .llm_worker import LLMWorker


class LLMClient:
    def __init__(self, worker: Optional[LLMWorker] = None):
        self.worker = worker
    
    async def generate(self, prompt: str, timeout: int = 30) -> str:
        if not self.worker:
            # Fallback when no worker is available
            return "Still working on that, try again."
        
        try:
            # Use timeout to prevent blocking
            return await asyncio.wait_for(
                self.worker.generate(prompt), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return "Still working on that, try again."
        except Exception as e:
            # Log error and return fallback
            print(f"LLM generation error: {e}")
            return "Still working on that, try again."
