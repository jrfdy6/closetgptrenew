FROM python:3.11-alpine

WORKDIR /app

# Copy requirements and install Python dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Copy the simple app.py (test if this works first)
COPY app.py ./app.py

# Debug: List files
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
ENV PYTHONPATH=/app

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 