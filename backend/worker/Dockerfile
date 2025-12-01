FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# The sys.path manipulation in main.py will handle finding backend/src/
# at runtime. Railway's build context may include parent directories,
# or the worker will use the fallback paths we coded.

# Run the worker
CMD ["python", "main.py"]

