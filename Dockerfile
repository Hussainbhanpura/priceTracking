# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary dependencies for Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxtst6 \
    libxrandr2 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .  
# Install Google Chrome
RUN pip3 install -r requirements.txt && \
    curl https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip -O && \
    unzip chromedriver_linux64.zip 

# Copy application files
COPY . .

# Set environment variables
ENV PATH="/root/.local/bin:${PATH}"

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "price_tracker:app"]
