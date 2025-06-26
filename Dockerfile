# Use a multi-stage build to keep the final image small
# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Setup Python backend
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Git and other dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next

# Expose ports for backend and frontend
EXPOSE 8001
EXPOSE 3000

# Set up a startup script
COPY start_docker.sh .
RUN chmod +x start_docker.sh

CMD ["./start_docker.sh"] 