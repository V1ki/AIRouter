# Multi-stage build for AI Router

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python backend with frontend
FROM python:3.11-slim

# Set environment to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies with retry and ignore signature issues temporarily
RUN set -ex \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app ./app
COPY scripts ./scripts

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy startup script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create .env file placeholder
RUN touch .env

# Expose ports
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]