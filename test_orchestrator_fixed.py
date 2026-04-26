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

# Now test the orchestrator by importing the actual models
async def test_orchestrator():
    print("Testing Jarvis Server Orchestrator...")
    
    # Import the actual models and orchestrator
    from app.api.models import RemoteRequest, RemoteResponse
    from app.orchestrator.orchestrator import Orchestrator
    
    orchestrator = Orchestrator()
    
    # Test cases with different request types
    test_cases = [
        {
            "input": "hello",
            "expected_type": "casual_chat",
            "description": "Casual greeting"
        },
        {
            "input": "what time is it?",
            "expected_type": "fact_query",
            "description": "Fact query about time"
        },
        {
            "input": "tell me the time",
            "expected_type": "direct_action",
            "description": "Direct action for time"
        },
        {
            "input": "remember my meeting at 3pm",
            "expected_type": "memory_query",
            "description": "Memory-related query"
        },
        {
            "input": "plan my day",
            "expected_type": "complex_reasoning",
            "description": "Complex reasoning request"
        },
        {
            "input": "search for weather",
            "expected_type": "direct_action",
            "description": "Direct action for search"
        },
        {
            "input": "what's the weather like?",
            "expected_type": "fact_query",
            "description": "Fact query about weather"
        },
        {
            "input": "hi",
            "expected_type": "casual_chat",
            "description": "Short casual chat"
        }
    ]
    
    print("\nOrchestrator Processing Tests:")
    for i, test_case in enumerate(test_cases, 1):
        request = RemoteRequest(input=test_case["input"])
        
        try:
            response = await orchestrator.process(request)
            actual_type = response.meta.get("request_type", "unknown")
            
            status = "✓" if actual_type == test_case["expected_type"] else "✗"
            print(f"  {status} Test {i}: {test_case['description']}")
            print(f"    Input: '{test_case['input']}'")
            print(f"    Expected: {test_case['expected_type']}, Got: {actual_type}")
            print(f"    Response: {response.text[:50]}...")
            print(f"    Latency: {response.meta.get('latency_ms', 0):.2f}ms")
            print()
            
        except Exception as e:
            print(f"  ✗ Test {i}: {test_case['description']} - ERROR: {e}")
            print()
    
    # Test with memory context
    print("Memory Context Test:")
    request_with_memory = RemoteRequest(
        input="what did we discuss?",
        memory_context=[
            {"content": "We discussed the project timeline", "type": "meeting"},
            {"content": "Deadline is next Friday", "type": "deadline"}
        ]
    )
    
    try:
        response = await orchestrator.process(request_with_memory)
        print(f"  ✓ Memory query processed")
        print(f"    Response: {response.text[:100]}...")
        print(f"    LLM used: {response.meta.get('llm_used', False)}")
        print()
    except Exception as e:
        print(f"  ✗ Memory query failed: {e}")
        print()
    
    # Test tool functionality
    print("Tool Functionality Tests:")
    tool_tests = [
        "tell me the time",
        "search for something",
        "what time is it?"
    ]
    
    for tool_input in tool_tests:
        request = RemoteRequest(input=tool_input)
        try:
            response = await orchestrator.process(request)
            print(f"  ✓ '{tool_input}' -> {response.text[:50]}...")
        except Exception as e:
            print(f"  ✗ '{tool_input}' failed: {e}")
    
    print("\nOrchestrator testing completed! ✓")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
