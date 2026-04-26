import time
import asyncio
from typing import List, Dict, Any
from ..api.models import RemoteRequest, RemoteResponse
from .classifier import RequestClassifier, RequestType
from ..tools.tool_registry import tool_registry
from ..tools.time_tool import TimeTool
from ..tools.web_search import WebSearchTool
from ..llm.llm_client import LLMClient
from ..llm.prompt_builder import build_prompt
from ..utils.logging import log_request


class Orchestrator:
    def __init__(self, llm_client=None):
        self.classifier = RequestClassifier()
        self.llm_client = llm_client or LLMClient()
        
        # Register tools
        tool_registry.register(TimeTool())
        tool_registry.register(WebSearchTool())
    
    async def process(self, request: RemoteRequest) -> RemoteResponse:
        start_time = time.time()
        
        # Classify the request
        request_type = self.classifier.classify(request.input)
        
        try:
            # Process based on request type
            if request_type == RequestType.CASUAL_CHAT:
                response_text = await self._handle_casual_chat(request.input)
                llm_used = False
            elif request_type == RequestType.DIRECT_ACTION:
                response_text = await self._handle_direct_action(request.input)
                llm_used = False
            elif request_type == RequestType.FACT_QUERY:
                response_text, llm_used = await self._handle_fact_query(request.input)
            elif request_type == RequestType.MEMORY_QUERY:
                response_text, llm_used = await self._handle_memory_query(request)
            elif request_type == RequestType.COMPLEX_REASONING:
                response_text, llm_used = await self._handle_complex_reasoning(request)
            else:
                response_text = "I'm not sure how to handle that request."
                llm_used = False
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log the request
            log_request(request_type.value, request.input, latency_ms, llm_used)
            
            return RemoteResponse(
                text=response_text,
                actions=[],
                meta={
                    "request_type": request_type.value,
                    "latency_ms": round(latency_ms, 2),
                    "llm_used": llm_used
                }
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            log_request(request_type.value, request.input, latency_ms, False)
            return RemoteResponse(
                text=f"Error processing request: {str(e)}",
                meta={
                    "request_type": request_type.value,
                    "latency_ms": round(latency_ms, 2),
                    "error": True
                }
            )
    
    async def _handle_casual_chat(self, input_text: str) -> str:
        casual_responses = {
            "hi": "Hello! How can I help you?",
            "hello": "Hi there! What can I do for you?",
            "hey": "Hey! What's up?",
            "thanks": "You're welcome!",
            "thank you": "You're welcome!",
            "bye": "Goodbye!",
            "goodbye": "See you later!",
        }
        
        text_lower = input_text.lower().strip()
        for key, response in casual_responses.items():
            if key in text_lower:
                return response
        
        return "Hi! How can I assist you today?"
    
    async def _handle_direct_action(self, input_text: str) -> str:
        # Try to use tools for direct actions
        if "time" in input_text.lower():
            time_tool = tool_registry.get_tool("time")
            return await time_tool.execute({})
        
        if "search" in input_text.lower():
            web_tool = tool_registry.get_tool("web_search")
            # Extract query from input (remove "search for", "search", etc.)
            query = input_text.lower().replace("search for", "").replace("search", "").strip()
            return await web_tool.execute({"query": query})
        
        return "I can help with that. What specific action would you like me to take?"
    
    async def _handle_fact_query(self, input_text: str) -> tuple[str, bool]:
        # Try tools first, fallback to LLM
        if "time" in input_text.lower():
            time_tool = tool_registry.get_tool("time")
            return await time_tool.execute({}), False
        
        # Use web search for fact queries that match patterns
        web_tool = tool_registry.get_tool("web_search")
        query = input_text.strip()
        return await web_tool.execute({"query": query}), False
    
    async def _handle_memory_query(self, request: RemoteRequest) -> tuple[str, bool]:
        # Extract memory context
        memory_texts = [str(ctx) for ctx in request.memory_context]
        
        # Use LLM with memory context
        prompt = build_prompt(request.input, memory_texts)
        try:
            response = await asyncio.wait_for(
                self.llm_client.generate(prompt), 
                timeout=10
            )
            return response, True
        except (asyncio.TimeoutError, Exception):
            return "Still working on that, try again.", False
    
    async def _handle_complex_reasoning(self, request: RemoteRequest) -> tuple[str, bool]:
        # Use LLM for complex reasoning
        memory_texts = [str(ctx) for ctx in request.memory_context]
        prompt = build_prompt(request.input, memory_texts)
        try:
            response = await asyncio.wait_for(
                self.llm_client.generate(prompt), 
                timeout=10
            )
            return response, True
        except (asyncio.TimeoutError, Exception):
            return "Still working on that, try again.", False
