from typing import Dict, Any, List
from ddgs import DDGS
from .base_tool import Tool


class WebSearchTool(Tool):
    name = "web_search"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        if not query:
            return {"success": False, "error": "Please provide a search query"}
        
        # Clean the query for better search results
        query = self._clean_query(query)
        
        try:
            # Perform search using DuckDuckGo
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=5))
                
                if not raw_results:
                    return {"success": False, "error": f"No results found for: {query}"}
                
                # Rank results by credibility and format
                ranked_results = self._rank_and_format_results(raw_results)
                
                return {
                    "success": True,
                    "query": query,
                    "results": ranked_results
                }
                
        except Exception as e:
            return {"success": False, "error": f"Search failed: {str(e)}"}
    
    def _clean_query(self, query: str) -> str:
        """Clean query by expanding abbreviations and removing question marks."""
        query = query.strip()
        
        # Remove question mark
        query = query.rstrip("?")
        
        # Expand common abbreviations
        abbreviations = {
            " cm ": " chief minister ",
            " pm ": " prime minister ",
            " ceo ": " chief executive officer ",
            " cto ": " chief technology officer ",
            " cfo ": " chief financial officer "
        }
        
        for abbr, full in abbreviations.items():
            query = query.replace(abbr, full)
        
        return query.strip()
    
    def _rank_and_format_results(self, raw_results: List[Dict]) -> List[Dict]:
        """Rank results by source credibility and format them."""
        # Source credibility scores (higher = more credible)
        credibility_scores = {
            "wikipedia.org": 10,
            "gov": 9,
            "edu": 8,
            "org": 7,
            "com": 5,
            "net": 4,
            "io": 3,
        }
        
        ranked = []
        for result in raw_results:
            href = result.get("href", "")
            score = 5  # default score
            
            # Calculate credibility score based on domain
            for domain, domain_score in credibility_scores.items():
                if domain in href.lower():
                    score = domain_score
                    break
            
            ranked.append({
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "href": href,
                "credibility_score": score
            })
        
        # Sort by credibility score (descending)
        ranked.sort(key=lambda x: x["credibility_score"], reverse=True)
        
        return ranked
