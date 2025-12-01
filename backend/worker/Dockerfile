FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Try to copy backend/src/ if it exists in the build context
# Railway's build context when root is backend/worker might include parent dirs
# If this fails, the sys.path manipulation in main.py will handle it
COPY ../src ./src 2>/dev/null || echo "Note: src/ not in build context, will use sys.path fix"

# Alternative: Create symlink if src exists in parent (for Railway's file structure)
# This handles cases where Railway includes parent directories in the container
RUN if [ -d "../src" ]; then \
        ln -sf ../src ./src || true; \
    fi

# The sys.path manipulation in main.py will handle finding backend/src/
# at runtime using multiple fallback paths if src/ isn't directly available.

# Run the worker
CMD ["python", "main.py"]

