#!/bin/bash

echo "=========================================="
echo "ICT Ultra v2: Algo Forge Edition"
echo "Starting platform services..."
echo "=========================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use!"
        return 1
    fi
    return 0
}

# Check required ports
echo "Checking ports..."
check_port 8001 || { echo "Backend port 8001 is busy"; exit 1; }
check_port 3000 || { echo "Frontend port 3000 is busy"; exit 1; }

# Start backend
echo ""
echo "Starting backend server on port 8001..."
cd backend
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
python main.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
sleep 5

# Check backend health
curl -s http://localhost:8001/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Backend is healthy"
else
    echo "✗ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo ""
echo "Starting frontend server on port 3000..."
cd ../frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Save PIDs for shutdown
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

echo ""
echo "=========================================="
echo "✓ ICT Ultra v2 is running!"
echo ""
echo "Backend API: http://localhost:8001"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "To stop: ./stop_platform.sh"
echo "=========================================="

# Keep script running
wait 