#!/bin/sh

# Docker Startup Script for ICT Ultra v2

echo "🚀 Starting ICT Ultra v2 Platform inside Docker..."

# Start backend
echo "▶️ Starting backend server..."
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"

# Start frontend
echo "▶️ Starting frontend server..."
cd /app/frontend
npm start &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $? 