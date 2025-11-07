#!/bin/bash

echo "🚀 Starting Video Subtitle Generator Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ .env file not found. Please create it and add your OpenAI API key."
    exit 1
fi

# Start the server
echo "🔧 Starting FastAPI server on http://localhost:8000"
python main.py