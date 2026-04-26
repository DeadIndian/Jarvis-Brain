from typing import Dict, Any
from duckduckgo_search import DDGS
from .base_tool import Tool


class WebSearchTool(Tool):
    name = "web_search"
    
    async def execute(self, input_data: Dict[str, Any]) -> str:
        query = input_data.get("query", "")
        if not query:
            return "Please provide a search query"
        
        try:
            # Perform search using DuckDuckGo
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                
                if not results:
                    return f"No results found for: {query}"
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append(f"- {result.get('title', '')}: {result.get('body', '')}")
                
                return f"Search results for '{query}':\n" + "\n".join(formatted_results)
                
        except Exception as e:
            return f"Search failed: {str(e)}"
