# Dockerfile for T34Bot

# Use a stable, slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app 

# Install system dependencies (if you need any extra libs, add here)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (use if you have a requirements.txt)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot code
COPY . .

# If your .env file is needed, mount it as a volume or copy it here (optional)
COPY .env .env

# Optional: if you have secrets or configs, mount them at runtime

# Default command to run the bot
CMD ["python", "run.py"]

# build/Update with => docker build -t t34bot:1.01 .

# run/start with => docker run --env-file .env --name t34bot_c --restart always t34bot:1.01

# TO push to dockerhub, use:
    # podman login docker.io
        #username: badzone
        #password: <your_password>
    # podman tag localhost/t34bot:1.01 docker.io/badzone/t34:1.01
    # podman push docker.io/badzone/t34:1.01
