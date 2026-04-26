import asyncio
import queue
import threading
from typing import Optional
from llama_cpp import Llama


class LLMWorker:
    def __init__(self, model_path: str = "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = None
        self.request_queue = queue.Queue()
        self.worker_thread = None
        self._running = False
        
        # Load model and start worker thread
        self._load_model()
        self._start_worker()
    
    def _load_model(self):
        """Load the llama.cpp model once at initialization."""
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,
                n_threads=4,  # Adjust to CPU cores
                n_batch=512
            )
            print(f"LLM model loaded from {self.model_path}")
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise
    
    def _start_worker(self):
        """Start the worker thread for processing inference requests."""
        self._running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("LLM worker thread started")
    
    def _worker_loop(self):
        """Worker thread loop that processes inference requests."""
        while self._running:
            try:
                # Get request from queue with timeout
                request = self.request_queue.get(timeout=1.0)
                
                if request is None:  # Shutdown signal
                    break
                
                prompt, future = request
                
                try:
                    # Run inference in worker thread
                    response = self._generate_sync(prompt)
                    future.set_result(response)
                except Exception as e:
                    future.set_exception(e)
                
                self.request_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker thread error: {e}")
    
    def _generate_sync(self, prompt: str) -> str:
        """Synchronous inference call - only called from worker thread."""
        if not self.llm:
            raise RuntimeError("Model not loaded")
        
        response = self.llm(
            prompt,
            max_tokens=80,
            temperature=0.6,
            top_p=0.9,
            stop=["User:", "\n\n"]
        )
        
        # Extract text from response
        return response["choices"][0]["text"].strip()
    
    async def generate(self, prompt: str) -> str:
        """Async interface for generating text."""
        if not self._running:
            raise RuntimeError("Worker not running")
        
        # Create future for result
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # Queue request for worker thread
        self.request_queue.put((prompt, future))
        
        # Wait for result
        return await future
    
    def shutdown(self):
        """Gracefully shutdown the worker thread."""
        self._running = False
        self.request_queue.put(None)  # Send shutdown signal
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        print("LLM worker shutdown complete")
