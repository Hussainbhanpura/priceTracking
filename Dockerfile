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

# Use Gunicorn as the WSGI server to serve the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "price_tracker:app"]
