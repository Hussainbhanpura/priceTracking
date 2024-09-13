# Use a more appropriate base image for a Python application
FROM python:3.10-slim

# Argument for setting the port
ARG PORT=443

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Update and install dependencies
RUN apt-get update && apt-get install -y python3-pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set environment variables (corrected PATH)
ENV PATH="/root/.local/bin:${PATH}"

# Set command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
