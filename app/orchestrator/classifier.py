from enum import Enum
from typing import List


class RequestType(Enum):
    DIRECT_ACTION = "direct_action"
    FACT_QUERY = "fact_query"
    MEMORY_QUERY = "memory_query"
    COMPLEX_REASONING = "complex_reasoning"
    CASUAL_CHAT = "casual_chat"


class RequestClassifier:
    def __init__(self):
        self.action_keywords = [
            "tell me", "show me", "get me", "find", "search", "look up",
            "what is", "what are", "who is", "when", "where", "why", "how"
        ]
        
        self.memory_keywords = [
            "remember", "recall", "what did i", "what was", "my", "i said",
            "i told you", "we discussed", "previous", "earlier"
        ]
        
        self.reasoning_keywords = [
            "plan", "summarize", "analyze", "compare", "evaluate", "explain",
            "recommend", "suggest", "decide", "choose", "pros and cons"
        ]
        
        self.casual_keywords = [
            "hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye",
            "how are you", "what's up", "nice", "cool", "awesome", "great"
        ]
        
        self.fact_query_patterns = [
            "capital of", "president of", "population of", "who is the", "what is the",
            "when was", "where is", "how many", "current", "latest", "definition of",
            "meaning of", "history of", "founded", "established", "born", "died",
            "ceo of", "founder of", "located in", "currency of", "language of"
        ]
    
    def classify(self, input_text: str) -> RequestType:
        text = input_text.lower().strip()
        
        # Check for casual chat first (highest priority)
        if any(keyword in text for keyword in self.casual_keywords):
            return RequestType.CASUAL_CHAT
        
        # Check for complex reasoning before memory queries
        if any(keyword in text for keyword in self.reasoning_keywords):
            return RequestType.COMPLEX_REASONING
        
        # Check for memory queries
        if any(keyword in text for keyword in self.memory_keywords):
            return RequestType.MEMORY_QUERY
        
        # Check for fact query patterns (specific factual lookups)
        if any(pattern in text for pattern in self.fact_query_patterns):
            return RequestType.FACT_QUERY
        
        # Check for direct actions/fact queries
        if any(keyword in text for keyword in self.action_keywords):
            # Differentiate between direct actions and fact queries
            if text.startswith(("tell me", "show me", "get me", "find", "search")):
                return RequestType.DIRECT_ACTION
            else:
                return RequestType.FACT_QUERY
        
        # Check for questions first
        if text.endswith("?"):
            return RequestType.FACT_QUERY
        
        # Default classification based on length and content
        if len(text) < 15:
            return RequestType.CASUAL_CHAT
        else:
            return RequestType.COMPLEX_REASONING
