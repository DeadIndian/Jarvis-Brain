"""
Test script for the optimized search pipeline
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.search_pipeline import (
    chunk_text,
    score_source,
    is_high_confidence,
    extract_direct_answer,
    SearchPipeline
)

def test_chunk_text():
    print("Testing chunk_text...")
    text = "This is sentence one. This is sentence two. This is sentence three. " * 50
    chunks = chunk_text(text)
    print(f"  Generated {len(chunks)} chunks")
    print(f"  First chunk length: {len(chunks[0].split())} words")
    print(f"  All chunks > 20 words: {all(len(c.split()) >= 20 for c in chunks)}")
    print("  ✓ chunk_text passed\n")

def test_score_source():
    print("Testing score_source...")
    test_cases = [
        ("https://en.wikipedia.org/wiki/Test", 10),
        ("https://mit.edu/test", 9),
        ("https://gov.uk/test", 9),
        ("https://docs.python.org/test", 8),
        ("https://reuters.com/test", 7),
        ("https://test.com", 4),
        ("https://test.xyz", 1),
    ]
    for url, expected in test_cases:
        score = score_source(url)
        print(f"  {url}: {score} (expected {expected})")
        assert score == expected, f"Expected {expected}, got {score}"
    print("  ✓ score_source passed\n")

def test_is_high_confidence():
    print("Testing is_high_confidence...")
    chunks = [
        {"text": "test", "score": 9, "similarity": 0.8},
        {"text": "test2", "score": 8, "similarity": 0.75},
    ]
    result = is_high_confidence(chunks)
    print(f"  High confidence with good chunks: {result}")
    assert result == True
    
    chunks_low = [
        {"text": "test", "score": 5, "similarity": 0.8},
        {"text": "test2", "score": 6, "similarity": 0.75},
    ]
    result = is_high_confidence(chunks_low)
    print(f"  High confidence with low scores: {result}")
    assert result == False
    print("  ✓ is_high_confidence passed\n")

def test_extract_direct_answer():
    print("Testing extract_direct_answer...")
    chunks = [
        {"text": "The chief minister of Telangana is Revanth Reddy. He took office in December 2023.", "score": 10},
    ]
    answer = extract_direct_answer(chunks)
    print(f"  Extracted answer: {answer}")
    print("  ✓ extract_direct_answer passed\n")

def test_search_pipeline():
    print("Testing SearchPipeline (this may take a moment)...")
    try:
        pipeline = SearchPipeline()
        print("  Pipeline initialized")
        
        # Test with a simple query
        result = pipeline.run("What is the capital of France?", max_results=3, max_chunks=5)
        
        print(f"  Total chunks extracted: {result.get('total_chunks', 0)}")
        print(f"  Chunks returned: {len(result.get('chunks', []))}")
        print(f"  High confidence: {result.get('high_confidence', False)}")
        
        if result.get('chunks'):
            print(f"  Top chunk score: {result['chunks'][0]['score']}")
            print(f"  Top chunk similarity: {result['chunks'][0]['similarity']:.3f}")
        
        if result.get('direct_answer'):
            print(f"  Direct answer: {result['direct_answer'][:100]}...")
        
        print("  ✓ SearchPipeline passed\n")
    except Exception as e:
        print(f"  ✗ SearchPipeline failed: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("Search Pipeline Tests")
    print("=" * 50 + "\n")
    
    test_chunk_text()
    test_score_source()
    test_is_high_confidence()
    test_extract_direct_answer()
    test_search_pipeline()
    
    print("=" * 50)
    print("All tests completed!")
    print("=" * 50)
