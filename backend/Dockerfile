# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main.py file
COPY main.py ./

# Expose port
EXPOSE 8080

# Run the FastAPI app
CMD ["python", "main.py"]
