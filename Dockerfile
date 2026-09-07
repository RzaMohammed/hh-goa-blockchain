# Multi-stage or lightweight Python image for Biometric Blockchain Verification Engine
FROM python:3.11-slim

# Install system dependencies for OpenCV and network tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Flask API and Web server port
EXPOSE 5000

# Set environment defaults
ENV PYTHONUNBUFFERED=1 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# Run API/Frontend server
CMD ["python", "frontend.py"]
