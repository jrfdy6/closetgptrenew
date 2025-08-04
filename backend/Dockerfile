FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with optimizations to prevent build crashes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the production app to the root
COPY src/app_full.py ./app.py

# Copy the rest of the source code for imports
COPY src/ ./src/

# Debug: List files to see what was copied
RUN ls -la

# Expose the port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the application using the production app
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"] 