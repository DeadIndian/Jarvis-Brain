from typing import List, Dict, Any


def build_prompt(input_text: str, context: List[str], search_results: List[Dict[str, Any]] = None) -> str:
    """Build a strict prompt for LLM with exact format requirements."""
    
    # Format context
    context_str = ""
    if context:
        context_str = "\n".join([f"- {ctx}" for ctx in context[:3]])
    
    # Format search results
    search_str = ""
    if search_results:
        search_str = "\n".join([
            f"[{r.get('credibility_score', 5)}/10] {r.get('title', '')}: {r.get('body', '')[:200]}"
            for r in search_results[:3]
        ])
    
    # Build strict prompt format
    prompt = f"""You are Jarvis reasoning module.

Rules:
* Max 80 tokens
* Be concise
* No filler
* Use ONLY provided context and search results
* If unsure, say "I don't know"

Context:
{context_str}

Search Results:
{search_str}

User:
{input_text}

Response:"""
    
    return prompt
