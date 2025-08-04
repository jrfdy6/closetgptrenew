FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install Python dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Copy the production app
COPY src/app_full.py ./app.py

# Copy source files
COPY src/ ./src/

# Debug: List files
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
ENV PYTHONPATH=/app

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 