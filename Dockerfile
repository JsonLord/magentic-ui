# Use the official Python 3.11 image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    openbox \
    x11vnc \
    novnc \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project to the container.
COPY . .

# Install Python dependencies.
RUN pip install --no-cache-dir .

# Install Playwright browsers and their dependencies
RUN playwright install --with-deps

# Run the application.
CMD ["magentic-ui", "--host", "0.0.0.0", "--port", "7860"]
