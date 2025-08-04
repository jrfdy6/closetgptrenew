FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for some Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Copy minimal requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy all files from the build context
COPY . .

# Copy the simplified production app to the root
RUN cp app_simple.py ./app.py

# Debug: List files in current directory
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
ENV PYTHONPATH=/app

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 