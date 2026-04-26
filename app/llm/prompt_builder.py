from typing import List


def build_prompt(input_text: str, context: List[str]) -> str:
    """Build a strict prompt for LLM with exact format requirements."""
    
    # Format context
    context_str = ""
    if context:
        context_str = "\n".join([f"- {ctx}" for ctx in context[:3]])
    
    # Build strict prompt format
    prompt = f"""You are Jarvis reasoning module.

Rules:
* Max 80 tokens
* Be concise
* No filler
* Use ONLY provided context
* If unsure, say "I don't know"

Context:
{context_str}

User:
{input_text}

Response:"""
    
    return prompt
