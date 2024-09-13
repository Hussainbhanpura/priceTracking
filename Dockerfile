# Use a Python slim base image
FROM python:3.10-slim

# Argument to set the port, default is 443
ARG PORT=443

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Update system packages and install pip
RUN apt-get update && apt-get install -y python3-pip

# Install Python dependencies with retry and verbose output for better debugging
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Copy all application files to the working directory
COPY . .

# Set the environment variable for the correct PATH
ENV PATH="/root/.local/bin:${PATH}"

# Command to start the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=${PORT}"]

