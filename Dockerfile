# Base image
FROM python:3.12-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    xvfb \
    x11vnc \
    openbox \
    supervisor \
    novnc \
    websockify \
    procps \
    xdg-utils \
    python3-xdg \
    x11-server-utils \
    ffmpeg \
    exiftool \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# Install uv (Python package manager)
RUN python3 -m pip install uv

# Add user's local bin to PATH
ENV PATH="/home/user/.local/bin:$PATH"

# Copy application code
COPY --chown=user . .

# Install Python dependencies
RUN uv pip install .

# Install frontend dependencies and build
WORKDIR /home/user/app/frontend
RUN npm install
RUN npm run build

# Install Playwright and its dependencies
WORKDIR /home/user/app
RUN npx playwright@1.51 install --with-deps chromium

# Expose the application port
EXPOSE 7860

# Set the command to start the application
CMD ["magentic-ui", "--host", "0.0.0.0", "--port", "7860", "--run-without-docker", "--appdir", "/home/user/app/.magentic_ui", "--reload"]
