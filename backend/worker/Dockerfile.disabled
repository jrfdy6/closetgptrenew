FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Note: Docker cannot COPY from parent directories when build context is backend/worker
# The sys.path manipulation in main.py will handle finding backend/src/ at runtime
# If Railway's build context includes parent directories, the worker will find src/ via sys.path
# If not, the fallback paths in main.py will attempt alternative locations

# Run the worker
CMD ["python", "main.py"]

