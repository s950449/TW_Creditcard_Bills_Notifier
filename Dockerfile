FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for keyring and PDF parsing
RUN apt-get update && apt-get install -y \
    libdbus-1-dev \
    libglib2.0-dev \
    gcc \
    pkg-config \
    dbus-x11 \
    libsecret-1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for WebUI
EXPOSE 8000

# Default command: run the WebUI
CMD ["python", "web/app.py"]
