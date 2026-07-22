# Use official Python image (3.11 without slim to avoid registry auth issues)
FROM python:3.11

# NUCLEAR CACHE BUSTER - Change this number on every deploy to break ALL caches
ARG CACHE_BUSTER=1766187700
RUN echo "CACHE BUSTER: $CACHE_BUSTER" && \
    echo "FORCE COMPLETE REBUILD - Railway Cache Bust v6" && \
    echo "Build ID: railway-$(date +%s)" && \
    echo "Commit: f873ccb86" && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    echo "Cache bust complete"

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

# NUCLEAR: Remove ALL Python bytecode and force timestamp update on ALL files
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete 2>/dev/null || true && \
    touch -a -m -t 202512192200 ./src/services/robust_outfit_generation_service.py && \
    touch -a -m -t 202512192200 ./src/services/filters/formality_tier_system.py && \
    echo "✅ Cleared all Python bytecode cache and updated file timestamps"

# Verify executable code rather than depending on temporary debug-log strings.
RUN python -m py_compile \
      ./src/services/robust_outfit_generation_service.py \
      ./src/services/diversity_filter_service.py \
      ./src/services/filters/formality_tier_system.py && \
    grep -q "async def generate_outfit" ./src/services/robust_outfit_generation_service.py && \
    grep -q "def _filter_by_tier" ./src/services/filters/formality_tier_system.py && \
    echo "✅ Outfit generation modules verified"

# Expose port (Railway will override with its own PORT)
EXPOSE 8080

# Run the FastAPI app with uvicorn using Railway's PORT env var
CMD ["sh", "-c", "python run.py"]
