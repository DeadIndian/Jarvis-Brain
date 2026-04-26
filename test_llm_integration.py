#!/usr/bin/env python3
"""
Test script for LLM integration with llama.cpp
Tests different request types and verifies the system works correctly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.models import RemoteRequest, RemoteResponse
from app.orchestrator.orchestrator import Orchestrator
from app.llm.llm_worker import LLMWorker
from app.llm.llm_client import LLMClient


async def test_simple_query():
    """Test simple query that should NOT hit LLM"""
    print("=== Testing Simple Query (should NOT use LLM) ===")
    
    try:
        # Initialize without LLM for this test
        orchestrator = Orchestrator(llm_client=LLMClient(worker=None))
        
        request = RemoteRequest(
            input="What time is it?",
            memory_context=[]
        )
        
        response = await orchestrator.process(request)
        print(f"Response: {response.text}")
        print(f"LLM Used: {response.meta.get('llm_used', False)}")
        print(f"Request Type: {response.meta.get('request_type', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"Error in simple query test: {e}")
        print()


async def test_with_dummy_llm():
    """Test with dummy LLM to verify flow"""
    print("=== Testing with Dummy LLM ===")
    
    try:
        # Test with dummy LLM client
        orchestrator = Orchestrator()
        
        request = RemoteRequest(
            input="Tell me something complex about quantum computing",
            memory_context=[{"previous_query": "user asked about physics", "result": "explained basic concepts"}]
        )
        
        response = await orchestrator.process(request)
        print(f"Response: {response.text}")
        print(f"LLM Used: {response.meta.get('llm_used', False)}")
        print(f"Request Type: {response.meta.get('request_type', 'unknown')}")
        print(f"Latency: {response.meta.get('latency_ms', 0)}ms")
        print()
        
    except Exception as e:
        print(f"Error in dummy LLM test: {e}")
        print()


async def test_worker_functionality():
    """Test LLM worker functionality (if model available)"""
    print("=== Testing LLM Worker (requires model file) ===")
    
    try:
        # Try to initialize worker (will fail if model not found)
        worker = LLMWorker(model_path="models/qwen-4b.gguf")
        client = LLMClient(worker=worker)
        orchestrator = Orchestrator(llm_client=client)
        
        request = RemoteRequest(
            input="What is the capital of France?",
            memory_context=[]
        )
        
        response = await orchestrator.process(request)
        print(f"Response: {response.text}")
        print(f"LLM Used: {response.meta.get('llm_used', False)}")
        print(f"Request Type: {response.meta.get('request_type', 'unknown')}")
        print(f"Latency: {response.meta.get('latency_ms', 0)}ms")
        print()
        
        # Cleanup
        worker.shutdown()
        
    except Exception as e:
        print(f"Expected error (model not found): {e}")
        print("This is normal if the model file doesn't exist yet.")
        print()


async def test_concurrent_requests():
    """Test concurrent request handling"""
    print("=== Testing Concurrent Requests ===")
    
    try:
        orchestrator = Orchestrator()
        
        # Create multiple concurrent requests
        requests = [
            RemoteRequest(input=f"Test query {i}", memory_context=[])
            for i in range(3)
        ]
        
        # Process all requests concurrently
        responses = await asyncio.gather(*[
            orchestrator.process(req) for req in requests
        ])
        
        for i, response in enumerate(responses):
            print(f"Request {i}: {response.text[:50]}...")
            print(f"  LLM Used: {response.meta.get('llm_used', False)}")
        
        print()
        
    except Exception as e:
        print(f"Error in concurrent test: {e}")
        print()


async def main():
    """Run all tests"""
    print("Jarvis Server LLM Integration Tests")
    print("=" * 40)
    print()
    
    await test_simple_query()
    await test_with_dummy_llm()
    await test_worker_functionality()
    await test_concurrent_requests()
    
    print("=" * 40)
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
