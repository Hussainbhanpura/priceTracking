# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

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
