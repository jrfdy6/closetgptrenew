# Use official Python image (3.11 without slim to avoid registry auth issues)
FROM python:3.11

# Force redeploy trigger - updated

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

# Copy the app.py, run.py, and minimal_debug_app.py files and necessary directories
COPY app.py ./
COPY run.py ./
COPY minimal_debug_app.py ./
COPY src/ ./src/

# Expose port (Railway will override with its own PORT)
EXPOSE 8080

# Run the FastAPI app with uvicorn using Railway's PORT env var
CMD ["sh", "-c", "python minimal_debug_app.py"]
