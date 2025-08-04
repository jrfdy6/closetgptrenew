# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY backend/ .

# Debug: Show what files we have
RUN echo "=== Files in /app ===" && ls -la && \
    echo "=== Python files ===" && find . -name "*.py" | head -10 && \
    echo "=== Checking app_full.py ===" && ls -la app_full.py

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the application using app_full.py directly
CMD ["uvicorn", "app_full:app", "--host", "0.0.0.0", "--port", "8080"] 