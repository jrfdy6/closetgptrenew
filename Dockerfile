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

# Copy the main application file
COPY backend/app_full.py app.py

# Copy all backend directories
COPY backend/src/ src/
COPY backend/app/ app/
COPY backend/services/ services/
COPY backend/routes/ routes/
COPY backend/models/ models/
COPY backend/utils/ utils/
COPY backend/core/ core/
COPY backend/data/ data/
COPY backend/middleware/ middleware/
COPY backend/custom_types/ custom_types/
COPY backend/jobs/ jobs/
COPY backend/scripts/ scripts/
COPY backend/tests/ tests/

# Debug: Show what files we have
RUN echo "=== Files in /app ===" && ls -la && \
    echo "=== Python files ===" && find . -name "*.py" | head -10

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 