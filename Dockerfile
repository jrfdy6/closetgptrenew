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

# Copy specific backend files to avoid nested directory confusion
COPY backend/app_full.py ./app.py
COPY backend/src/ ./src/
COPY backend/app/ ./app/
COPY backend/services/ ./services/
COPY backend/routes/ ./routes/
COPY backend/models/ ./models/
COPY backend/utils/ ./utils/
COPY backend/core/ ./core/
COPY backend/data/ ./data/
COPY backend/middleware/ ./middleware/
COPY backend/custom_types/ ./custom_types/
COPY backend/jobs/ ./jobs/
COPY backend/scripts/ ./scripts/
COPY backend/tests/ ./tests/

RUN ls -la

EXPOSE 8080
ENV PORT=8080
ENV PYTHONPATH=/app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 