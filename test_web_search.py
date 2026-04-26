import asyncio
from ddgs import DDGS
import json

async def test_search():
    queries = [
        "chief minister of telangana",
    ]
    
    for query in queries:
        print(f"\n--- Testing query: '{query}' ---")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=1))
                
                if not results:
                    print(f"No results found")
                else:
                    print(f"Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"\nResult {i}:")
                        print(f"Available fields: {list(result.keys())}")
                        print(f"Full result:")
                        print(json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
