#!/bin/bash

# ICT Ultra v2: Algo Forge Edition - Startup Script
# This script starts the backend and frontend services

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "  ___ ___ _____ _   _ _ _             ___ "
echo " |_ _/ __|_   _| | | | | |_ _ _ __ _ | __|"
echo "  | | (__  | | | |_| | |  _| '_/ _\` || _| "
echo " |___\___| |_|  \___/|_|\__|_| \__,_||_|  "
echo "                                          "
echo -e "${GREEN}Algo Forge Edition${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    if command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$1 "
        return $?
    elif command -v ss &> /dev/null; then
        ss -tuln | grep -q ":$1 "
        return $?
    else
        # Fallback to lsof if available
        if command -v lsof &> /dev/null; then
            lsof -i ":$1" &> /dev/null
            return $?
        fi
    fi
    # If no tool is available, assume port is free
    return 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓ Python 3 found${NC}"
elif command_exists python; then
    PYTHON_CMD="python"
    echo -e "${GREEN}✓ Python found${NC}"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js.${NC}"
    exit 1
fi

# Check npm or pnpm
if command_exists pnpm; then
    NPM_CMD="pnpm"
    echo -e "${GREEN}✓ pnpm found${NC}"
elif command_exists npm; then
    NPM_CMD="npm"
    echo -e "${GREEN}✓ npm found${NC}"
else
    echo -e "${RED}✗ npm or pnpm not found. Please install npm.${NC}"
    exit 1
fi

# Check if ports are available
echo -e "${YELLOW}Checking ports...${NC}"
if check_port 8001; then
    echo -e "${RED}✗ Port 8001 is already in use. Please close the application using this port.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Port 8001 is available${NC}"
fi

if check_port 3000; then
    echo -e "${RED}✗ Port 3000 is already in use. Please close the application using this port.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Port 3000 is available${NC}"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend
echo -e "${YELLOW}Starting backend...${NC}"
cd backend || exit
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows Git Bash
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Install requirements
echo -e "${YELLOW}Installing backend requirements...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend requirements installed${NC}"

# Start backend server
echo -e "${YELLOW}Starting backend server...${NC}"
$PYTHON_CMD main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend server started with PID $BACKEND_PID${NC}"

# Give backend time to start
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 5

# Start frontend
echo -e "${YELLOW}Starting frontend...${NC}"
cd ../frontend || exit

# Install dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
$NPM_CMD install
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Start frontend server
echo -e "${YELLOW}Starting frontend server...${NC}"
$NPM_CMD run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend server started with PID $FRONTEND_PID${NC}"

# Return to root directory
cd ..

# Save PIDs for later use
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

# Final instructions
echo ""
echo -e "${GREEN}ICT Ultra v2 is now running!${NC}"
echo -e "Backend API: ${BLUE}http://localhost:8001${NC}"
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "To stop the servers, run: ${YELLOW}./stop.sh${NC}"
echo ""

# Keep the script running to catch Ctrl+C
echo -e "${YELLOW}Press Ctrl+C to stop the servers${NC}"
trap "echo -e '${RED}Stopping servers...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 