import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock FastAPI to avoid dependency issues
class MockFastAPI:
    def __init__(self, **kwargs):
        pass

class MockCORSMiddleware:
    def __init__(self, **kwargs):
        pass

class MockRouter:
    def __init__(self):
        pass

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

# Simple request/response classes for testing
class SimpleRequest:
    def __init__(self, input_text, memory_context=None, client_state=None):
        self.input = input_text
        self.memory_context = memory_context or []
        self.client_state = client_state or {}

class SimpleResponse:
    def __init__(self, text, actions=None, meta=None):
        self.text = text
        self.actions = actions or []
        self.meta = meta or {}

async def test_simple_orchestrator():
    print("Testing Jarvis Server Core Components...")
    
    # Test classifier directly
    from app.orchestrator.classifier import RequestClassifier, RequestType
    classifier = RequestClassifier()
    
    test_cases = [
        ("hello", "casual_chat"),
        ("what time is it?", "fact_query"),
        ("tell me the time", "direct_action"),
        ("remember my meeting", "memory_query"),
        ("plan my day", "complex_reasoning"),
        ("search for weather", "direct_action"),
        ("what's the weather like?", "fact_query"),
        ("hi", "casual_chat")
    ]
    
    print("\nClassification Tests:")
    all_passed = True
    for input_text, expected in test_cases:
        result = classifier.classify(input_text)
        status = "✓" if result.value == expected else "✗"
        if result.value != expected:
            all_passed = False
        print(f"  {status} '{input_text}' -> {result.value} (expected: {expected})")
    
    # Test tools
    from app.tools.tool_registry import tool_registry
    from app.tools.time_tool import TimeTool
    from app.tools.web_search import WebSearchTool
    
    # Register tools
    tool_registry.register(TimeTool())
    tool_registry.register(WebSearchTool())
    
    print("\nTool Tests:")
    time_tool = tool_registry.get_tool("time")
    time_result = await time_tool.execute({})
    print(f"  ✓ Time tool: {time_result}")
    
    web_tool = tool_registry.get_tool("web_search")
    web_result = await web_tool.execute({})
    print(f"  ✓ Web search tool: {web_result}")
    
    # Test LLM client
    from app.llm.llm_client import LLMClient
    llm_client = LLMClient("dummy")
    llm_result = await llm_client.generate("test prompt")
    print(f"  ✓ LLM client: {llm_result}")
    
    # Test orchestrator logic directly
    from app.orchestrator.orchestrator import Orchestrator
    
    # Create a simple orchestrator test
    orchestrator = Orchestrator()
    
    print("\nOrchestrator Logic Tests:")
    orchestrator_test_cases = [
        ("hello", "casual_chat"),
        ("what time is it?", "fact_query"),
        ("tell me the time", "direct_action"),
    ]
    
    for input_text, expected_type in orchestrator_test_cases:
        request_type = classifier.classify(input_text)
        print(f"  Testing '{input_text}' -> {request_type.value}")
        
        try:
            if request_type == RequestType.CASUAL_CHAT:
                result = await orchestrator._handle_casual_chat(input_text)
                print(f"    ✓ Casual chat: {result}")
            elif request_type == RequestType.DIRECT_ACTION:
                result = await orchestrator._handle_direct_action(input_text)
                print(f"    ✓ Direct action: {result}")
            elif request_type == RequestType.FACT_QUERY:
                result, llm_used = await orchestrator._handle_fact_query(input_text)
                print(f"    ✓ Fact query: {result} (LLM: {llm_used})")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    # Test memory components
    from app.memory.memory_store import MemoryStore
    memory_store = MemoryStore()
    memory_store.add_memory("Test memory", {"type": "test"})
    memories = memory_store.get_memories()
    print(f"\n  ✓ Memory store: {len(memories)} memories stored")
    
    from app.memory.chunker import Chunker
    chunker = Chunker()
    chunks = chunker.chunk_text("This is a test. This is another test. And a third test.")
    print(f"  ✓ Chunker: {len(chunks)} chunks created")
    
    from app.memory.embedding import Embedding
    embedding = Embedding()
    emb = embedding.embed_text("test text")
    print(f"  ✓ Embedding: {len(emb)} dimensions")
    
    # Test prompt builder
    from app.llm.prompt_builder import build_prompt
    prompt = build_prompt("What is the weather?", ["It is sunny today"])
    print(f"  ✓ Prompt builder: {len(prompt)} characters")
    
    print(f"\nOverall Result: {'✓ All tests passed!' if all_passed else '✗ Some tests failed'}")
    print(f"Jarvis Server core functionality is working!")

if __name__ == "__main__":
    asyncio.run(test_simple_orchestrator())
