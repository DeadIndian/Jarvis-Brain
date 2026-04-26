import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .utils.logging import setup_logging
from .config import config
import atexit

app = FastAPI(
    title="Jarvis Server",
    description="Central intelligence layer for distributed assistant system",
    version="1.0.0"
)

setup_logging()

# Initialize LLM system through config
config.initialize_llm(model_path="models/Qwen3-4B-Q6_K.gguf")

# Register cleanup
def cleanup():
    config.shutdown()

atexit.register(cleanup)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Jarvis Server is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
