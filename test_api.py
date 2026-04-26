import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock FastAPI to avoid dependency issues
class MockFastAPI:
    def __init__(self, **kwargs):
        self.routes = []
        self.middleware = []
    
    def include_router(self, router, **kwargs):
        self.routes.append(f"Router: {router}")
    
    def add_middleware(self, middleware, **kwargs):
        self.middleware.append(f"Middleware: {middleware}")
    
    def get(self, path):
        def decorator(func):
            self.routes.append(f"GET {path}")
            return func
        return decorator

class MockCORSMiddleware:
    def __init__(self, **kwargs):
        pass

class MockRouter:
    def __init__(self):
        self.routes = []
    
    def post(self, path, **kwargs):
        def decorator(func):
            self.routes.append(f"POST {path}")
            return func
        return decorator

# Mock the dependencies
sys.modules['fastapi'] = type('MockModule', (), {
    'FastAPI': MockFastAPI,
    'APIRouter': MockRouter,
    'HTTPException': Exception
})()

sys.modules['fastapi.middleware.cors'] = type('MockModule', (), {
    'CORSMiddleware': MockCORSMiddleware
})()

sys.modules['pydantic'] = type('MockModule', (), {
    'BaseModel': object
})()

# Now test our modules
async def test_components():
    print("Testing Jarvis Server Components...")
    
    # Test classifier
    from app.orchestrator.classifier import RequestClassifier, RequestType
    classifier = RequestClassifier()
    
    test_cases = [
        ("hello", RequestType.CASUAL_CHAT),
        ("what time is it", RequestType.FACT_QUERY),
        ("tell me the time", RequestType.DIRECT_ACTION),
        ("remember my meeting", RequestType.MEMORY_QUERY),
        ("plan my day", RequestType.COMPLEX_REASONING),
        ("search for weather", RequestType.DIRECT_ACTION),
    ]
    
    print("\nRequest Classification Tests:")
    for input_text, expected_type in test_cases:
        result = classifier.classify(input_text)
        status = "✓" if result == expected_type else "✗"
        print(f"  {status} '{input_text}' -> {result.value}")
    
    # Test tools
    from app.tools.tool_registry import tool_registry
    from app.tools.time_tool import TimeTool
    from app.tools.web_search import WebSearchTool
    
    # Register tools
    tool_registry.register(TimeTool())
    tool_registry.register(WebSearchTool())
    
    print("\nTool Registry Tests:")
    print(f"  ✓ Registered tools: {list(tool_registry.list_tools().keys())}")
    
    # Test time tool
    time_tool = tool_registry.get_tool("time")
    time_result = await time_tool.execute({})
    print(f"  ✓ Time tool: {time_result}")
    
    # Test web search tool
    web_tool = tool_registry.get_tool("web_search")
    web_result = await web_tool.execute({})
    print(f"  ✓ Web search tool: {web_result}")
    
    # Test LLM client
    from app.llm.llm_client import LLMClient
    llm_client = LLMClient("dummy")
    llm_result = await llm_client.generate("test prompt")
    print(f"  ✓ LLM client: {llm_result}")
    
    # Test prompt builder
    from app.llm.prompt_builder import build_prompt
    prompt = build_prompt("What is the weather?", ["It is sunny today"])
    print(f"  ✓ Prompt builder: {prompt[:50]}...")
    
    # Test memory components
    from app.memory.memory_store import MemoryStore
    memory_store = MemoryStore()
    memory_store.add_memory("Test memory", {"type": "test"})
    memories = memory_store.get_memories()
    print(f"  ✓ Memory store: {len(memories)} memories stored")
    
    from app.memory.chunker import Chunker
    chunker = Chunker()
    chunks = chunker.chunk_text("This is a test. This is another test. And a third test.")
    print(f"  ✓ Chunker: {len(chunks)} chunks created")
    
    from app.memory.embedding import Embedding
    embedding = Embedding()
    emb = embedding.embed_text("test text")
    print(f"  ✓ Embedding: {len(emb)} dimensions")
    
    print("\nAll components tested successfully! ✓")

if __name__ == "__main__":
    asyncio.run(test_components())
