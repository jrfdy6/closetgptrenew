FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code (contains the actual production app)
COPY . .

# Debug: List files to see what was copied
RUN ls -la

# Expose the port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the application using the actual production app
CMD ["sh", "-c", "uvicorn src.app_full:app --host 0.0.0.0 --port $PORT"] 