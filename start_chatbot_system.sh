#!/bin/bash

# PCTE College Chatbot - Complete System Startup Script
# This script starts both the backend API and frontend React app

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/tarandeepsingh/Desktop/Chatbot project 2"
CHATBOT_DIR="$PROJECT_ROOT/chatbot"
FRONTEND_DIR="$PROJECT_ROOT/front-end"

echo -e "${BLUE}🎓 PCTE College Chatbot System Startup${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo -e "${RED}❌ $name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Step 1: Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check conda environment
if ! conda info --envs | grep -q pytorch; then
    echo -e "${RED}❌ Conda environment 'pytorch' not found${NC}"
    echo "Please create the environment with: conda create -n pytorch python=3.10"
    exit 1
fi

# Check Node.js
if ! command -v node > /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

# Check if API key is configured
if [ -f "$CHATBOT_DIR/.env" ]; then
    if grep -q "your_google_api_key_here" "$CHATBOT_DIR/.env"; then
        echo -e "${YELLOW}⚠️  Google API key not configured (will use local intents only)${NC}"
    else
        echo -e "${GREEN}✅ Google API key configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found (will use local intents only)${NC}"
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"
echo ""

# Step 2: Clean up any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"

# Kill existing backend processes
if check_port 8000; then
    echo "Port 8000 is free"
else
    echo "Killing processes on port 8000..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Kill existing frontend processes  
if check_port 5173; then
    echo "Port 5173 is free"
else
    echo "Killing processes on port 5173..."
    lsof -ti :5173 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo -e "${GREEN}✅ Cleanup completed${NC}"
echo ""

# Step 3: Start Backend API Server
echo -e "${YELLOW}🚀 Starting Backend API Server...${NC}"
cd "$CHATBOT_DIR"

# Activate conda environment and start server in background
nohup bash -c "source $(conda info --base)/etc/profile.d/conda.sh && conda activate pytorch && python api_server.py" > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
if wait_for_service "http://localhost:8000/health" "Backend API"; then
    echo -e "${GREEN}✅ Backend API Server started successfully (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}📍 Backend running at: http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend API Server failed to start${NC}"
    echo "Check logs: tail -f $CHATBOT_DIR/backend.log"
    exit 1
fi

echo ""

# Step 4: Start Frontend React App
echo -e "${YELLOW}🚀 Starting Frontend React App...${NC}"
cd "$FRONTEND_DIR"

# Start frontend in background
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
if wait_for_service "http://localhost:5173" "Frontend App"; then
    echo -e "${GREEN}✅ Frontend React App started successfully (PID: $FRONTEND_PID)${NC}"
    echo -e "${BLUE}📍 Frontend running at: http://localhost:5173${NC}"
else
    echo -e "${RED}❌ Frontend React App failed to start${NC}"
    echo "Check logs: tail -f $FRONTEND_DIR/frontend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""

# Step 5: Final Status and Instructions
echo -e "${GREEN}🎉 PCTE College Chatbot System Started Successfully!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   🌐 Web Interface: ${GREEN}http://localhost:5173${NC}"
echo -e "   🔧 API Server:    ${GREEN}http://localhost:8000${NC}"
echo -e "   📊 Health Check:  ${GREEN}http://localhost:8000/health${NC}"
echo ""
echo -e "${BLUE}📝 Process Information:${NC}"
echo -e "   Backend PID:  $BACKEND_PID"
echo -e "   Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${BLUE}📜 Log Files:${NC}"
echo -e "   Backend:  $CHATBOT_DIR/backend.log"
echo -e "   Frontend: $FRONTEND_DIR/frontend.log"
echo ""
echo -e "${YELLOW}💡 Usage Tips:${NC}"
echo -e "   • Open ${GREEN}http://localhost:5173${NC} in your browser"
echo -e "   • Test API: ${GREEN}curl http://localhost:8000/health${NC}"
echo -e "   • View logs: ${GREEN}tail -f backend.log${NC} or ${GREEN}tail -f frontend.log${NC}"
echo ""
echo -e "${YELLOW}🛑 To stop the system:${NC}"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   Or run: ${GREEN}./stop_chatbot_system.sh${NC}"
echo ""
echo -e "${GREEN}✨ Happy Chatting! ✨${NC}"

# Save PIDs for cleanup script
echo "$BACKEND_PID" > "$PROJECT_ROOT/backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/frontend.pid"