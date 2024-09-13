# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Update system packages and install pip
RUN apt-get update && apt-get install -y python3-pip

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files to the working directory
COPY . .

# Set the environment variable for the correct PATH
ENV PATH="/root/.local/bin:${PATH}"

# Use the shell form of CMD to correctly expand environment variables
CMD uvicorn price_tracker:app --host 0.0.0.0 --port ${PORT}
