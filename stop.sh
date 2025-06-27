#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}=======================================${NC}"
echo -e "${RED}Stopping ICT Ultra v2: Algo Forge Edition${NC}"
echo -e "${RED}=======================================${NC}"

# Check if tmux is installed and if our session exists
if command -v tmux &> /dev/null && tmux has-session -t ict-ultra-v2 2>/dev/null; then
    echo -e "${YELLOW}Stopping tmux session...${NC}"
    tmux kill-session -t ict-ultra-v2
    echo -e "${GREEN}✓ Tmux session stopped${NC}"
else
    # Try to stop by process ID if not running in tmux
    echo -e "${YELLOW}Stopping services...${NC}"
    
    # Find and kill Python backend processes
    BACKEND_PIDS=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')
    if [ -n "$BACKEND_PIDS" ]; then
        echo -e "${YELLOW}Stopping backend processes: $BACKEND_PIDS${NC}"
        kill $BACKEND_PIDS 2>/dev/null
        echo -e "${GREEN}✓ Backend processes stopped${NC}"
    else
        echo -e "${YELLOW}No backend processes found${NC}"
    fi
    
    # Find and kill Next.js frontend processes
    FRONTEND_PIDS=$(ps aux | grep "[n]ode.*next" | awk '{print $2}')
    if [ -n "$FRONTEND_PIDS" ]; then
        echo -e "${YELLOW}Stopping frontend processes: $FRONTEND_PIDS${NC}"
        kill $FRONTEND_PIDS 2>/dev/null
        echo -e "${GREEN}✓ Frontend processes stopped${NC}"
    else
        echo -e "${YELLOW}No frontend processes found${NC}"
    fi
fi

echo -e "${GREEN}ICT Ultra v2 has been stopped.${NC}"
