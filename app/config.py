"""
Configuration and dependency injection for Jarvis Server
"""

import os
from typing import Optional
from .llm.llm_worker import LLMWorker
from .llm.llm_client import LLMClient


class ServerConfig:
    """Global server configuration and dependency container"""
    
    def __init__(self):
        self.llm_worker: Optional[LLMWorker] = None
        self.llm_client: Optional[LLMClient] = None
        self._initialized = False
        self.api_key = os.getenv("JARVIS_API_KEY", "your-secret-api-key-change-this")
    
    def initialize_llm(self, model_path: str = "models/Qwen3-4B-Q6_K.gguf"):
        """Initialize LLM worker and client"""
        if self._initialized:
            return
        
        try:
            self.llm_worker = LLMWorker(model_path=model_path)
            self.llm_client = LLMClient(worker=self.llm_worker)
            print("LLM system initialized successfully")
        except Exception as e:
            print(f"Failed to initialize LLM system: {e}")
            print("Running without LLM capabilities")
            self.llm_client = LLMClient(worker=None)
        
        self._initialized = True
    
    def get_llm_client(self) -> LLMClient:
        """Get the LLM client instance"""
        if not self._initialized:
            self.initialize_llm()
        return self.llm_client
    
    def shutdown(self):
        """Gracefully shutdown LLM worker"""
        if self.llm_worker:
            self.llm_worker.shutdown()
            print("LLM worker shutdown complete")


# Global configuration instance
config = ServerConfig()
