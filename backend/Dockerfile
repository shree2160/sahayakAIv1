# Sahayak AI - Backend Dockerfile
# ================================
# For deployment on Render, Railway, etc.

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download VOSK Hindi model
RUN mkdir -p vosk_models && \
    cd vosk_models && \
    curl -LO https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip && \
    unzip vosk-model-small-hi-0.22.zip && \
    rm vosk-model-small-hi-0.22.zip

# Copy application code
COPY . .

# Create audio directory
RUN mkdir -p audio_files

# Expose port (Render sets $PORT env var)
EXPOSE 8000

# Run the application using gunicorn for production
# Render requires the app to listen on the port provided by $PORT
CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --graceful-timeout 30
