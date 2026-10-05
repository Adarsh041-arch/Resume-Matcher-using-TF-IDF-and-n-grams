FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for build tools and PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY . .

# Expose FastAPI application port
EXPOSE 8000

# Run API and Web Dashboard
CMD ["python", "main.py", "--serve", "--host", "0.0.0.0", "--port", "8000"]
