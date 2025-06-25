#!/bin/bash

# ICT Ultra v2: Algo Forge Edition - Stop Script
# This script stops the backend and frontend services

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${RED}"
echo "  ___ ___ _____ _   _ _ _             ___ "
echo " |_ _/ __|_   _| | | | | |_ _ _ __ _ | __|"
echo "  | | (__  | | | |_| | |  _| '_/ _\` || _| "
echo " |___\___| |_|  \___/|_|\__|_| \__,_||_|  "
echo "                                          "
echo -e "${YELLOW}Stopping Services${NC}"
echo ""

# Function to check if a process is running
is_process_running() {
    if [ -z "$1" ]; then
        return 1
    fi
    
    if ps -p "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to kill process by PID
kill_process() {
    if [ -z "$1" ]; then
        return
    fi
    
    if is_process_running "$1"; then
        echo -e "${YELLOW}Stopping process with PID $1...${NC}"
        kill "$1" 2>/dev/null
        sleep 1
        if is_process_running "$1"; then
            echo -e "${RED}Process did not stop gracefully, forcing...${NC}"
            kill -9 "$1" 2>/dev/null
        fi
        echo -e "${GREEN}✓ Process stopped${NC}"
    else
        echo -e "${BLUE}Process with PID $1 is not running${NC}"
    fi
}

# Check if PID files exist
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    kill_process "$BACKEND_PID"
    rm -f logs/backend.pid
else
    echo -e "${YELLOW}Backend PID file not found${NC}"
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    kill_process "$FRONTEND_PID"
    rm -f logs/frontend.pid
else
    echo -e "${YELLOW}Frontend PID file not found${NC}"
fi

# Additional cleanup for Node.js processes
echo -e "${YELLOW}Checking for any remaining Node.js processes...${NC}"
if command -v pkill &> /dev/null; then
    pkill -f "node.*frontend" 2>/dev/null
elif command -v killall &> /dev/null; then
    killall -q node 2>/dev/null
else
    echo -e "${YELLOW}pkill/killall not available, skipping additional cleanup${NC}"
fi

echo ""
echo -e "${GREEN}All services have been stopped${NC}"
echo "" 