FROM python:3.11-slim

WORKDIR /app

# Install only essential dependencies first
RUN pip install fastapi uvicorn

# Copy the simple app file
COPY simple_app.py .

# Debug: Show what files we have
RUN echo "=== Files in /app ===" && ls -la

EXPOSE 8080
ENV PORT=8080

CMD ["uvicorn", "simple_app:app", "--host", "0.0.0.0", "--port", "8080"] 