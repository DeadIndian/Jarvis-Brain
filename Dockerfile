FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy model files (optional - can also mount as volume)
# COPY models/ ./models/

# Create __init__.py files to make directories proper Python packages
RUN touch app/__init__.py
RUN touch app/api/__init__.py
RUN touch app/orchestrator/__init__.py
RUN touch app/memory/__init__.py
RUN touch app/tools/__init__.py
RUN touch app/llm/__init__.py
RUN touch app/utils/__init__.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
