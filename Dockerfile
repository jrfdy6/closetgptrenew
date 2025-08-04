FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend directory
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ .

# Use the main app as entrypoint - copy from backend directory
COPY backend/app_full.py ./app.py

RUN ls -la

EXPOSE 8080
ENV PORT=8080
ENV PYTHONPATH=/app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 