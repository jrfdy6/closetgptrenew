# Use official Python image (3.11 without slim to avoid registry auth issues)
FROM python:3.11

# NUCLEAR CACHE BUSTER - Change this number on every deploy to break ALL caches
ARG CACHE_BUSTER=1760405200
RUN echo "CACHE BUSTER: $CACHE_BUSTER" && echo "METADATA FIX DEPLOYMENT - This will never be cached because ARG changes"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Upgrade pip first to avoid network issues
RUN python -m pip install --upgrade pip

# Install large packages separately to avoid BrokenPipeError
RUN pip install --no-cache-dir --default-timeout=100 onnxruntime==1.22.1 opencv-python-headless==4.12.0.88 || pip install --no-cache-dir --default-timeout=100 onnxruntime==1.22.1 opencv-python-headless==4.12.0.88

# Install remaining dependencies with retry logic
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt || pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# AGGRESSIVE CACHE BUST - Force complete file copy with no cache
# Adding timestamp forces Docker to rebuild this layer and all subsequent layers
RUN echo "Build timestamp: $(date +%s)" > /tmp/build_marker.txt

# Copy the app.py, run.py, and minimal_debug_app.py files and necessary directories
COPY app.py ./
COPY run.py ./
COPY minimal_debug_app.py ./
COPY src/ ./src/

# Verify files were copied (this will fail if cache is used with old files)
RUN echo "Verifying new code..." && \
    grep -q "HARD FILTER ENTRY" ./src/services/robust_outfit_generation_service.py && \
    echo "✅ New code verified: debug logging present" || \
    (echo "❌ Old code detected: debug logging missing" && exit 1)

# Expose port (Railway will override with its own PORT)
EXPOSE 8080

# Run the FastAPI app with uvicorn using Railway's PORT env var
CMD ["sh", "-c", "python run.py"]
