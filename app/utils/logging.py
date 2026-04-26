import logging
import sys
from datetime import datetime


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def log_request(request_type: str, input_text: str, latency_ms: float, llm_used: bool = False):
    logger = logging.getLogger("jarvis")
    logger.info(f"Request - Type: {request_type}, Input: {input_text[:50]}..., "
                f"Latency: {latency_ms:.2f}ms, LLM: {llm_used}")
