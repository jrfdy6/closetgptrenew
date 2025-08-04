FROM python:3.11-alpine

WORKDIR /app

# Install Python dependencies only
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Copy the simple app.py
COPY app.py ./app.py

# Copy the production app
COPY app_full.py ./app_full.py

# Copy source files
COPY src/ ./src/

# Debug: List files in current directory
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
ENV PYTHONPATH=/app

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 