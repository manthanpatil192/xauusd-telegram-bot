FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for matplotlib and font rendering
RUN apt-get update && apt-get install -y \
    build-essential \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run Telegram Bot
CMD ["python", "main.py"]
