# Use official Python image (3.11 without slim to avoid registry auth issues)
FROM python:3.11

# NUCLEAR CACHE BUSTER - Change this number on every deploy to break ALL caches
ARG CACHE_BUSTER=1766183000
RUN echo "CACHE BUSTER: $CACHE_BUSTER" && echo "FORCE COMPLETE REBUILD - Clear Bytecode Cache v4"

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

# Remove all Python bytecode cache to force fresh imports
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete 2>/dev/null || true && \
    echo "✅ Cleared all Python bytecode cache"

# Verify files were copied (this will fail if cache is used with old files)
RUN echo "Verifying GENERATE_OUTFIT entry point..." && \
    grep -q "GENERATE_OUTFIT CALLED" ./src/services/robust_outfit_generation_service.py && \
    echo "✅ generate_outfit entry point verified" || \
    (echo "❌ generate_outfit entry point MISSING - build failed!" && exit 1) && \
    echo "Verifying PHASE 1 START marker..." && \
    grep -q "PHASE 1 START: occasion" ./src/services/robust_outfit_generation_service.py && \
    echo "✅ PHASE 1 START marker verified" || \
    (echo "❌ PHASE 1 START marker MISSING - build failed!" && exit 1) && \
    echo "Verifying TIER FILTER CHECK marker..." && \
    grep -q "TIER FILTER CHECK: Occasion" ./src/services/robust_outfit_generation_service.py && \
    echo "✅ TIER FILTER CHECK marker verified" || \
    (echo "❌ TIER FILTER CHECK marker MISSING - build failed!" && exit 1) && \
    echo "Verifying tier filter blocking logic..." && \
    grep -q "BLOCKED.*keyword" ./src/services/filters/formality_tier_system.py && \
    echo "✅ Tier filter blocking logic verified" || \
    (echo "❌ Tier filter blocking logic MISSING - build failed!" && exit 1)

# Expose port (Railway will override with its own PORT)
EXPOSE 8080

# Run the FastAPI app with uvicorn using Railway's PORT env var
CMD ["sh", "-c", "python run.py"]
