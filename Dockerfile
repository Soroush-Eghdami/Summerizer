# Use Python 3.11 alpine image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port that Flask runs on
EXPOSE 5000

# Health check
HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1

# Run the Flask application
CMD ["python", "server.py"]
