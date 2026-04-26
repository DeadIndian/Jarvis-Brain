# Jarvis Server

Central intelligence layer for distributed assistant system with local LLM integration.

## Production Docker Setup (Recommended)

Follow these steps to deploy Jarvis Server in production using Docker.

### Step 1: Clone the Repository

```bash
git clone https://github.com/DeadIndian/Jarvis-Brain.git
cd Jarvis-Brain
```

### Step 2: Generate a Secure API Key

Generate a secure random API key for authentication:

```bash
# Using OpenSSL
export JARVIS_API_KEY=$(openssl rand -hex 32)

# Or using Python
export JARVIS_API_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Verify the key was generated
echo $JARVIS_API_KEY
```

### Step 3: Download the LLM Model

Create the models directory and download the Llama 3.2 1B Instruct model (Q4 quantized, ~0.8GB):

```bash
# Create models directory
mkdir -p models

# Download the model
cd models
wget https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf

# Verify the download
ls -lh Llama-3.2-1B-Instruct-Q4_K_M.gguf
# Should show approximately 0.8GB

cd ..
```

### Step 4: Build the Docker Image

```bash
docker build -t jarvis-server .
```

### Step 5: Run the Container

Run the container with the model volume mounted and API key configured:

```bash
docker run -d \
  --name jarvis-server \
  -v $(pwd)/models:/app/models \
  -p 8000:8000 \
  -e JARVIS_API_KEY=$JARVIS_API_KEY \
  -e LLM_MODEL_PATH=models/Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  --memory=2g \
  --cpus=2 \
  jarvis-server
```

**Optional**: Restrict CORS origins to your specific domains:

```bash
docker run -d \
  --name jarvis-server \
  -v $(pwd)/models:/app/models \
  -p 8000:8000 \
  -e JARVIS_API_KEY=$JARVIS_API_KEY \
  -e LLM_MODEL_PATH=models/Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  -e CORS_ORIGINS=https://your-app-domain.com,https://another-domain.com \
  --memory=2g \
  --cpus=2 \
  jarvis-server
```

### Step 6: Verify the Deployment

Check that the container is running:

```bash
docker ps | grep jarvis-server
```

Test the API with your generated API key:

```bash
# Test a simple query
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $JARVIS_API_KEY" \
  -d '{"input": "hello", "memory_context": []}'

# Test LLM query
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $JARVIS_API_KEY" \
  -d '{"input": "What is the capital of France?", "memory_context": []}'
```

### Step 7: Manage the Container

```bash
# View logs
docker logs -f jarvis-server

# Stop the container
docker stop jarvis-server

# Start the container
docker start jarvis-server

# Remove the container
docker rm jarvis-server
```

### Environment Variables

- **JARVIS_API_KEY** (required): Secure random API key for authentication
- **LLM_MODEL_PATH** (optional): Model file path (default: `models/Llama-3.2-1B-Instruct-Q4_K_M.gguf`)
- **CORS_ORIGINS** (optional): Comma-separated list of allowed CORS origins (default: `*`)

## Overview

Jarvis Server is a deterministic-first backend service that acts as central intelligence layer for a distributed assistant system. It prioritizes tool-based execution over LLM-driven orchestration and is designed to be modular, CPU-only, and compatible with small local models.

**✅ LLM Integration**: Tuned for Llama 3.2 1B model with llama.cpp for local inference  
**🚀 Non-blocking**: Async architecture with request queuing  
**🔧 Production Ready**: Docker support with comprehensive error handling

## Architecture

### Core Components

- **API Layer**: FastAPI-based REST API with `/process` endpoint
- **Orchestrator**: Core logic that routes requests based on deterministic classification
- **Classifier**: Rule-based request classification (no ML/LLM)
- **Tool System**: Extensible tool registry with time and web search tools
- **Memory Layer**: Structured memory storage and retrieval (future write API)
- **LLM Layer**: Integrated Llama 3.2 1B model with llama.cpp worker thread

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
│   └── Llama-3.2-1B-Instruct-Q4_K_M.gguf
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Security

The Jarvis Server requires API key authentication to prevent unauthorized access. All requests to protected endpoints must include a valid API key in the `X-API-Key` header.

**Security Best Practices**:

- Generate a strong, random API key (at least 32 characters) using the commands in Step 2
- Set `CORS_ORIGINS` to your specific app domains in production
- Use environment variables or secrets management for storing the API key
- Rotate API keys periodically
- Never expose API keys in client-side code

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

**Headers:**

```
X-API-Key: your-secure-random-api-key-here
Content-Type: application/json
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

**Error Response (Invalid API Key):**

```json
{
	"detail": "Invalid API key"
}
```

## Model Information

**Current Model**: Llama-3.2-1B-Instruct-Q4_K_M.gguf

- **Size**: ~0.8GB
- **Quantization**: Q4_K_M (4-bit quantized)
- **Context Window**: 4096 tokens
- **Max Response**: 80 tokens
- **Inference**: CPU-only, single-threaded queue

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
python -c "from app.llm.llm_worker import LLMWorker; LLMWorker('models/Llama-3.2-1B-Instruct-Q4_K_M.gguf')"

# Check model file integrity
file models/Llama-3.2-1B-Instruct-Q4_K_M.gguf
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
Error: Model path does not exist: models/Llama-3.2-1B-Instruct-Q4_K_M.gguf

```

**Solution**: Ensure model file is downloaded to `models/` directory and `LLM_MODEL_PATH` points to the correct filename

### Still Seeing Qwen Model Path In Logs

If logs still show `models/Qwen3-4B-Q6_K.gguf`, your running container is using an older image/code version.

```bash
# Stop and remove old container (if running)
docker stop jarvis-server || true
docker rm jarvis-server || true

# Rebuild with latest code
docker build --no-cache -t jarvis-server .

# Ensure Llama model file exists locally
ls -lh models/Llama-3.2-1B-Instruct-Q4_K_M.gguf

# Start with explicit model path
docker run -d \
  --name jarvis-server \
  -v $(pwd)/models:/app/models \
  -p 8000:8000 \
  -e JARVIS_API_KEY=$JARVIS_API_KEY \
  -e LLM_MODEL_PATH=models/Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  jarvis-server

# Verify startup picked the right path
docker logs jarvis-server | grep "Initializing LLM with model path"
```

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
