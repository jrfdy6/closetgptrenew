# Use slim base image to reduce size
FROM python:3.11-slim

WORKDIR /app

# Install only system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements first for better layer caching
COPY requirements-minimal.txt .

# Install Python dependencies with no cache
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Use environment variable for port
CMD ["uvicorn", "src.ultra_minimal:app", "--host", "0.0.0.0", "--port", "8080"] 