FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend
COPY backend/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py file
COPY app.py ./app.py

# Copy backend source files
COPY backend/src/ ./src/

# Debug: List files to see what was copied
RUN ls -la

# Expose the port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the application using configurable port
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"] 