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

# Copy the main.py file
COPY main.py ./

# Expose port (Railway automatically maps to $PORT)
ENV PORT=8080
EXPOSE $PORT

# Run the FastAPI app
CMD ["python", "main.py"]
