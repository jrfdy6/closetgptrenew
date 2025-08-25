# Use official Python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY src ./src

# Expose port (Railway automatically maps to $PORT)
ENV PORT=8000
EXPOSE $PORT

# Run the FastAPI app
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
