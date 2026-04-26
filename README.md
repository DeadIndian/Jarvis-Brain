# Jarvis Server

Central intelligence layer for distributed assistant system.

## Overview

Jarvis Server is a deterministic-first backend service that acts as the central intelligence layer for a distributed assistant system. It prioritizes tool-based execution over LLM-driven orchestration and is designed to be modular, CPU-only, and compatible with small local models.

## Architecture

### Core Components

- **API Layer**: FastAPI-based REST API with `/process` endpoint
- **Orchestrator**: Core logic that routes requests based on deterministic classification
- **Classifier**: Rule-based request classification (no ML/LLM)
- **Tool System**: Extensible tool registry with time and web search tools
- **Memory Layer**: Structured memory storage and retrieval (future write API)
- **LLM Layer**: Abstract LLM client (dummy implementation, ready for llama.cpp/Ollama)

### Request Types

1. **CASUAL_CHAT**: Simple greetings and casual conversation
2. **DIRECT_ACTION**: Commands like "tell me", "show me", "find"
3. **FACT_QUERY**: Questions seeking factual information
4. **MEMORY_QUERY**: Requests involving stored memory/context
5. **COMPLEX_REASONING**: Tasks requiring analysis, planning, summarization

## Project Structure

```
server/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── models.py          # Request/Response models
│   │   └── routes.py          # API endpoints
│   ├── orchestrator/
│   │   ├── orchestrator.py   # Core orchestration logic
│   │   └── classifier.py      # Deterministic classification
│   ├── tools/
│   │   ├── base_tool.py       # Tool interface
│   │   ├── tool_registry.py   # Tool registration system
│   │   ├── time_tool.py       # Time tool
│   │   └── web_search.py      # Web search tool (stub)
│   ├── llm/
│   │   ├── llm_client.py      # LLM client abstraction
│   │   └── prompt_builder.py  # Prompt template system
│   ├── memory/
│   │   ├── memory_store.py    # Memory storage
│   │   ├── markdown_loader.py # Markdown file loading
│   │   ├── chunker.py         # Text chunking
│   │   └── embedding.py       # Text embedding (stub)
│   └── utils/
│       └── logging.py         # Structured logging
├── requirements.txt
├── Dockerfile
└── README.md
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

## Docker Setup

```bash
# Build the image
docker build -t jarvis-server .

# Run the container
docker run -p 8000:8000 jarvis-server
```

## Development

### Local Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run syntax validation
python test_syntax.py

# Run component tests
python test_simple.py

# Test API endpoints (requires dependencies)
python test_api.py
```

## Design Principles

1. **Deterministic-First**: Use rules and tools before LLM
2. **Modular**: Clean separation between components
3. **CPU-Only**: No GPU dependencies
4. **Async**: All operations are non-blocking
5. **Future-Proof**: Ready for LLM integration and streaming

## Next Steps

- Integrate real LLM backend (llama.cpp or Ollama)
- Implement memory write API
- Add streaming responses
- Enhance tool calling via LLM
- Add multi-step planning capabilities

## Dependencies

- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- HTTPX 0.25.2
- NumPy 1.24.3

## Performance

- All endpoints async
- Tool-first execution (LLM as fallback)
- Structured logging with latency tracking
- Graceful error handling
