# Use Python 3.12
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for ffmpeg + audio processing)
RUN apt-get update && apt-get install -y ffmpeg gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "server.py"]
