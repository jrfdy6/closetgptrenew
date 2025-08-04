FROM python:3.11-alpine

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Copy the app file directly
COPY app_simple.py ./app.py

# Debug: List files
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 