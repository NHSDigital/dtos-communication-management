# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV HOST=${HOST} \
    DBNAME=${DBNAME} \
    USER=${USER}

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY connect_db.py .

# Set default command
CMD ["python", "connect_db.py"]
