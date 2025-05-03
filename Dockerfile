FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Expose port for the Flask app
EXPOSE 5001

# Create start script for gunicorn with eventlet worker
RUN echo '#!/bin/sh\n\
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 --log-level info app:app' > /app/start.sh && \
    chmod +x /app/start.sh

# Command to run the application with gunicorn
CMD ["/app/start.sh"]