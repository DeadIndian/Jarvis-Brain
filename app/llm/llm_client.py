from typing import Optional
import asyncio
from .llm_worker import LLMWorker


FALLBACK_RESPONSE = "Still working on that, try again."


class LLMClient:
    def __init__(self, worker: Optional[LLMWorker] = None):
        self.worker = worker

    def is_available(self) -> bool:
        return self.worker is not None
    
    async def generate(self, prompt: str, timeout: int = 30) -> tuple[str, bool]:
        if not self.worker:
            # Fallback when no worker is available
            return FALLBACK_RESPONSE, False
        
        try:
            # Use timeout to prevent blocking
            response = await asyncio.wait_for(
                self.worker.generate(prompt), 
                timeout=timeout
            )
            return response, True
        except asyncio.TimeoutError:
            return FALLBACK_RESPONSE, False
        except Exception as e:
            # Log error and return fallback
            print(f"LLM generation error: {e}")
            return FALLBACK_RESPONSE, False
