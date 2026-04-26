"""
Optimized web search pipeline with semantic similarity and confidence gating
"""
import re
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

logger = logging.getLogger(__name__)


class Embedder:
    """Handles text embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        if not texts:
            return np.array([])
        return self.model.encode(texts, convert_to_numpy=True)


def chunk_text(text: str, max_words: int = 200, min_words: int = 20) -> List[str]:
    """
    Split text into chunks by sentences/paragraphs
    
    Args:
        text: Input text to chunk
        max_words: Maximum words per chunk
        min_words: Minimum words per chunk (discard smaller chunks)
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_words = 0
    
    for sentence in sentences:
        words = sentence.split()
        word_count = len(words)
        
        # If sentence itself is too long, split it
        if word_count > max_words:
            # Flush current chunk if exists
            if current_chunk and current_words >= min_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_words = 0
            
            # Split long sentence
            for i in range(0, len(words), max_words):
                sub_chunk = ' '.join(words[i:i + max_words])
                if len(sub_chunk.split()) >= min_words:
                    chunks.append(sub_chunk)
        else:
            # Add to current chunk
            if current_words + word_count <= max_words:
                current_chunk.extend(words)
                current_words += word_count
            else:
                # Flush current chunk
                if current_words >= min_words:
                    chunks.append(' '.join(current_chunk))
                current_chunk = words
                current_words = word_count
    
    # Flush remaining chunk
    if current_words >= min_words:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def score_source(url: str) -> int:
    """
    Score URL by source credibility
    
    Args:
        url: URL to score
    
    Returns:
        Credibility score (1-10)
    """
    url_lower = url.lower()
    
    # High credibility sources
    if "wikipedia.org" in url_lower:
        return 10
    if ".edu" in url_lower:
        return 9
    if ".gov" in url_lower or "gov." in url_lower:
        return 9
    
    # Known documentation sites
    if any(domain in url_lower for domain in ["docs.python.org", "developer.mozilla.org", "w3.org"]):
        return 8
    
    # News sites
    if any(domain in url_lower for domain in ["reuters.com", "apnews.com", "bbc.com", "nytimes.com"]):
        return 7
    if any(domain in url_lower for domain in ["cnn.com", "theguardian.com", "washingtonpost.com"]):
        return 6
    
    # Medium credibility
    if ".org" in url_lower:
        return 5
    if ".com" in url_lower:
        return 4
    
    # Low credibility
    if ".xyz" in url_lower or ".top" in url_lower or ".tk" in url_lower:
        return 1
    
    # Default
    return 3


def fetch_page_text(url: str, timeout: int = 10) -> str:
    """
    Fetch and extract text from a URL
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
    
    Returns:
        Extracted text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return ""


def is_high_confidence(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.7) -> bool:
    """
    Determine if chunks have high confidence for direct answer
    
    Args:
        chunks: List of chunks with similarity scores
        similarity_threshold: Minimum similarity for high confidence
    
    Returns:
        True if high confidence (can skip LLM)
    """
    if len(chunks) < 2:
        return False
    
    # Check if top 2 chunks have high source scores
    top_two = chunks[:2]
    if not (top_two[0]['score'] >= 8 and top_two[1]['score'] >= 8):
        return False
    
    # Check if top chunks have high semantic similarity
    if top_two[0]['similarity'] < similarity_threshold:
        return False
    
    return True


def extract_direct_answer(chunks: List[Dict[str, Any]]) -> str:
    """
    Extract direct answer from highest scoring chunk
    
    Args:
        chunks: Ranked chunks
    
    Returns:
        Direct answer (first 1-2 sentences)
    """
    if not chunks:
        return "No answer found."
    
    best_chunk = chunks[0]['text']
    
    # Extract first 1-2 sentences
    sentences = re.split(r'(?<=[.!?])\s+', best_chunk)
    answer = ' '.join(sentences[:2])
    
    return answer


class SearchPipeline:
    """
    Optimized search pipeline with semantic similarity and confidence gating
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedder = Embedder(model_name)
        logger.info("SearchPipeline initialized")
    
    def run(self, query: str, max_results: int = 5, max_chunks: int = 8) -> Dict[str, Any]:
        """
        Run the search pipeline
        
        Args:
            query: Search query
            max_results: Number of search results to fetch
            max_chunks: Maximum chunks to return
        
        Returns:
            Dict with chunks, confidence, and direct answer if available
        """
        logger.info(f"Running search pipeline for query: {query}")
        
        try:
            # Step 1: Web search
            urls = self._search_web(query, max_results)
            if not urls:
                logger.warning("No search results found")
                return {"chunks": [], "high_confidence": False, "error": "No search results"}
            
            logger.info(f"Found {len(urls)} URLs")
            
            # Step 2: Fetch page content
            all_chunks = []
            for url in urls:
                text = fetch_page_text(url)
                if text:
                    chunks = chunk_text(text)
                    source_score = score_source(url)
                    for chunk in chunks:
                        all_chunks.append({
                            "text": chunk,
                            "source": url,
                            "score": source_score
                        })
            
            if not all_chunks:
                logger.warning("No chunks extracted from pages")
                return {"chunks": [], "high_confidence": False, "error": "No content extracted"}
            
            logger.info(f"Extracted {len(all_chunks)} chunks total")
            
            # Step 3: Embed and rank
            ranked_chunks = self._rank_chunks(query, all_chunks, max_chunks)
            
            # Step 4: Confidence check
            high_conf = is_high_confidence(ranked_chunks)
            logger.info(f"High confidence: {high_conf}")
            
            # Step 5: Direct answer if high confidence
            direct_answer = None
            if high_conf:
                direct_answer = extract_direct_answer(ranked_chunks)
                logger.info(f"Direct answer extracted: {direct_answer[:100]}...")
            
            return {
                "chunks": ranked_chunks,
                "high_confidence": high_conf,
                "direct_answer": direct_answer,
                "total_chunks": len(all_chunks)
            }
        
        except Exception as e:
            logger.error(f"Search pipeline error: {e}")
            return {"chunks": [], "high_confidence": False, "error": str(e)}
    
    def _search_web(self, query: str, max_results: int) -> List[str]:
        """Perform web search and return URLs"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return [r.get("href", "") for r in results if r.get("href")]
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def _rank_chunks(self, query: str, chunks: List[Dict], max_chunks: int) -> List[Dict]:
        """
        Rank chunks by semantic similarity and source score
        
        Args:
            query: Search query
            chunks: List of chunks with text and source score
            max_chunks: Maximum chunks to return
        
        Returns:
            Ranked chunks with similarity scores
        """
        if not chunks:
            return []
        
        # Embed query and chunks
        texts = [query] + [c['text'] for c in chunks]
        embeddings = self.embedder.encode(texts)
        
        query_embedding = embeddings[0]
        chunk_embeddings = embeddings[1:]
        
        # Compute cosine similarity
        similarities = np.dot(chunk_embeddings, query_embedding) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
        )
        
        # Add similarity to chunks
        for i, chunk in enumerate(chunks):
            chunk['similarity'] = float(similarities[i])
        
        # Sort by combined score (similarity + source score)
        chunks.sort(key=lambda x: (x['similarity'] * 0.6 + x['score'] * 0.4), reverse=True)
        
        # Return top chunks
        return chunks[:max_chunks]
    
    def build_llm_prompt(self, query: str, chunks: List[Dict]) -> str:
        """
        Build compact prompt for LLM with ranked chunks
        
        Args:
            query: Original query
            chunks: Ranked chunks
        
        Returns:
            Formatted prompt
        """
        prompt = f"Question: {query}\n\nSources:\n\n"
        
        for i, chunk in enumerate(chunks, 1):
            prompt += f"[Score {chunk['score']} - {chunk['source']}]\n{chunk['text']}\n\n"
        
        prompt += "Task: Answer using the highest credibility sources above. Be concise and accurate."
        
        return prompt
