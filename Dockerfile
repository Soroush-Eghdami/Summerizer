# Use Python 3.11 alpine image as alternative to slim
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies for Alpine
RUN apk add --no-cache \
    build-base \
    curl \
    gcc \
    musl-dev

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
