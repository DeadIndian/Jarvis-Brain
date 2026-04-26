# Jarvis Server

Central intelligence layer for distributed assistant system with local LLM integration.

## Overview

Jarvis Server is a deterministic-first backend service that acts as central intelligence layer for a distributed assistant system. It prioritizes tool-based execution over LLM-driven orchestration and is designed to be modular, CPU-only, and compatible with small local models.

**✅ LLM Integration**: Now includes Qwen 4B model with llama.cpp for local inference  
**🚀 Non-blocking**: Async architecture with request queuing  
**🔧 Production Ready**: Docker support with comprehensive error handling

## Architecture

### Core Components

- **API Layer**: FastAPI-based REST API with `/process` endpoint
- **Orchestrator**: Core logic that routes requests based on deterministic classification
- **Classifier**: Rule-based request classification (no ML/LLM)
- **Tool System**: Extensible tool registry with time and web search tools
- **Memory Layer**: Structured memory storage and retrieval (future write API)
- **LLM Layer**: Integrated Qwen 4B model with llama.cpp worker thread

### Request Types

1. **CASUAL_CHAT**: Simple greetings and casual conversation
2. **DIRECT_ACTION**: Commands like "tell me", "show me", "find"
3. **FACT_QUERY**: Questions seeking factual information
4. **MEMORY_QUERY**: Requests involving stored memory/context
5. **COMPLEX_REASONING**: Tasks requiring analysis, planning, summarization

## Project Structure

```
Jarvis-Brain/
├── app/                    # Main application code
│   ├── main.py             # FastAPI application
│   ├── api/               # API routes and models
│   ├── orchestrator/       # Request orchestration
│   ├── tools/             # Tool implementations
│   ├── llm/               # LLM integration
│   ├── memory/             # Memory management
│   ├── config.py           # Configuration
│   └── utils/             # Utilities
├── models/                # LLM model files
│   └── Qwen3-4B-Q6_K.gguf
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Quick Start

### Option 1: Docker (Recommended)

#### Step 1: Install Model Locally

```bash
# Create models directory
mkdir -p models

# Download Qwen 4B model (3.1GB)
cd models
wget https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q6_K.gguf

# Verify model downloaded
ls -lh Qwen3-4B-Q6_K.gguf
# Should show: -rw-r--r-- 1 user user 3.1G [date] Qwen3-4B-Q6_K.gguf
```

#### Step 2: Build and Run Docker

```bash
# Build Docker image
docker build -t jarvis-server .

# Run with model volume mounted
docker run -v $(pwd)/models:/app/models -p 8000:8000 jarvis-server
```

#### Step 3: Verify Installation

```bash
# Test simple query (no LLM)
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{"input": "hello", "memory_context": []}'

# Test LLM query
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{"input": "What is the capital of France?", "memory_context": []}'
```

### Option 2: Local Development

#### Step 1: Setup Environment

```bash
# Clone repository
git clone https://github.com/DeadIndian/Jarvis-Brain.git
cd Jarvis-Brain

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Install Model

```bash
# Create models directory and download model
mkdir -p models
cd models
wget https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q6_K.gguf
cd ..
```

#### Step 3: Run Server

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### POST /api/process

**Request:**

```json
{
	"input": "what time is it?",
	"memory_context": [],
	"client_state": {}
}
```

**Response:**

```json
{
	"text": "Current time: 2026-04-26 18:12:48",
	"actions": [],
	"meta": {
		"request_type": "fact_query",
		"latency_ms": 15.2,
		"llm_used": false
	}
}
```

## Model Information

**Current Model**: Qwen3-4B-Q6_K.gguf

- **Size**: 3.1GB
- **Quantization**: Q6_K (6-bit quantized)
- **Context Window**: 4096 tokens
- **Max Response**: 80 tokens
- **Inference**: CPU-only, single-threaded queue

## Docker Advanced Usage

### Custom Model Path

```bash
# Mount different model directory
docker run -v /path/to/your/models:/app/models -p 8000:8000 jarvis-server
```

### Development Mode

```bash
# Mount source code for live reload
docker run -v $(pwd):/app -v $(pwd)/models:/app/models -p 8000:8000 jarvis-server uvicorn app.main:app --reload
```

### Production Mode

```bash
# Run with resource limits
docker run --memory=2g --cpus=2 -v $(pwd)/models:/app/models -p 8000:8000 jarvis-server
```

## Development

### Testing

```bash
# Run syntax validation
python test_syntax.py

# Run component tests
python test_simple.py

# Test LLM integration
python test_llm_integration.py

# Test API endpoints (requires dependencies)
python test_api.py
```

### Model Management

```bash
# Test model loading
python -c "from app.llm.llm_worker import LLMWorker; LLMWorker('models/Qwen3-4B-Q6_K.gguf')"

# Check model file integrity
file models/Qwen3-4B-Q6_K.gguf
```

## Design Principles

1. **Deterministic-First**: Use rules and tools before LLM
2. **Modular**: Clean separation between components
3. **CPU-Only**: No GPU dependencies
4. **Async**: All operations are non-blocking
5. **Production-Ready**: Docker support with error handling

## Performance

- **Non-blocking**: All endpoints async with proper queuing
- **Tool-first**: Direct execution (LLM as fallback)
- **Single Model**: Memory efficient with request queuing
- **Timeout Protection**: 10s limit with graceful fallbacks
- **Concurrent Safe**: Multiple requests queued properly

## Dependencies

- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- HTTPX 0.25.2
- llama-cpp-python 0.2.0
- NumPy 1.24.3

## Troubleshooting

### Model Not Found

```
Error: Model path does not exist: models/Qwen3-4B-Q6_K.gguf
```

**Solution**: Ensure model file is downloaded to `models/` directory

### Docker Volume Issues

```
Error: Failed to load model
```

**Solution**: Verify volume mount path and model file permissions

### Memory Issues

```
Error: Killed
```

**Solution**: Increase Docker memory limit or use smaller model

## Next Steps

- [ ] Add streaming responses
- [ ] Implement memory write API
- [ ] Enhance tool calling via LLM
- [ ] Add multi-step planning capabilities
- [ ] Support multiple model switching
