# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py file and necessary directories
COPY app.py ./
COPY src/ ./src/

# Expose port (Railway will override with its own PORT)
EXPOSE 8080

# Run the FastAPI app with Gunicorn using Railway's PORT env var
CMD ["sh", "-c", "gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8080} --log-level debug"]
