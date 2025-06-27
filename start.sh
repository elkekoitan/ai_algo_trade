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

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}tmux is not installed. Running in standard mode.${NC}"
    
    # Start backend in background
    echo -e "${GREEN}Starting backend server...${NC}"
    cd backend && python main.py &
    BACKEND_PID=$!
    
    # Start frontend
    echo -e "${GREEN}Starting frontend server...${NC}"
    cd frontend && npm run dev
    
    # Kill backend when frontend is stopped
    kill $BACKEND_PID
else
    # Create a new tmux session
    echo -e "${GREEN}Starting services in tmux session...${NC}"
    SESSION="ict-ultra-v2"
    
    # Kill existing session if it exists
    tmux kill-session -t $SESSION 2>/dev/null
    
    # Create new session with backend
    tmux new-session -d -s $SESSION -n "backend" "cd backend && python main.py"
    
    # Create window for frontend
    tmux new-window -t $SESSION:1 -n "frontend" "cd frontend && npm run dev"
    
    # Create window for logs
    tmux new-window -t $SESSION:2 -n "logs" "tail -f backend/logs/app.log"
    
    # Select the backend window
    tmux select-window -t $SESSION:0
    
    # Attach to the session
    echo -e "${GREEN}ICT Ultra v2 started in tmux session '${SESSION}'${NC}"
    echo -e "${YELLOW}Use 'tmux attach -t ${SESSION}' to view the session${NC}"
    echo -e "${YELLOW}Press Ctrl+B then number (0,1,2) to switch windows${NC}"
    echo -e "${YELLOW}Press Ctrl+B then D to detach from session${NC}"
    
    tmux attach -t $SESSION
    
    echo -e "${GREEN}Stopping ICT Ultra v2...${NC}"
    tmux kill-session -t $SESSION
fi

echo -e "${GREEN}ICT Ultra v2 has been stopped.${NC}" 