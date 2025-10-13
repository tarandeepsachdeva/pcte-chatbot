#!/bin/bash

# PCTE College Chatbot - System Stop Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/tarandeepsingh/Desktop/Chatbot project 2"

echo -e "${BLUE}🛑 PCTE College Chatbot System Shutdown${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to kill process by PID
kill_process() {
    local pid=$1
    local name=$2
    
    if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo -e "${YELLOW}⏹️  Stopping $name (PID: $pid)...${NC}"
        kill $pid
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}🔫 Force stopping $name...${NC}"
            kill -9 $pid
        fi
        echo -e "${GREEN}✅ $name stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  $name was not running${NC}"
    fi
}

# Stop processes using saved PIDs
if [ -f "$PROJECT_ROOT/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/backend.pid")
    kill_process "$BACKEND_PID" "Backend API Server"
    rm -f "$PROJECT_ROOT/backend.pid"
fi

if [ -f "$PROJECT_ROOT/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/frontend.pid")
    kill_process "$FRONTEND_PID" "Frontend React App"
    rm -f "$PROJECT_ROOT/frontend.pid"
fi

# Kill any remaining processes on the ports
echo -e "${YELLOW}🧹 Cleaning up any remaining processes...${NC}"

# Kill processes on port 8000 (backend)
if lsof -i :8000 > /dev/null 2>&1; then
    echo "Killing remaining processes on port 8000..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

# Kill processes on port 5173 (frontend)
if lsof -i :5173 > /dev/null 2>&1; then
    echo "Killing remaining processes on port 5173..."
    lsof -ti :5173 | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}✅ Cleanup completed${NC}"
echo ""
echo -e "${GREEN}🎉 PCTE College Chatbot System Stopped Successfully!${NC}"
echo -e "${BLUE}💡 To restart the system, run: ./start_chatbot_system.sh${NC}"