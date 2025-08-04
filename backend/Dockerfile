FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for some Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    libjpeg-turbo-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the build context
COPY . .

# Copy the production app to the root
RUN cp src/app.py ./app.py

# Debug: List files in current directory
RUN ls -la

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
ENV PYTHONPATH=/app

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"] 