FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Python, MySQL, and Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/app/
COPY run.py ./
COPY db/ /app/db/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]
