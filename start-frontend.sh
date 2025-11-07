#!/bin/bash

echo "🚀 Starting Video Subtitle Generator Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run setup.sh first."
    exit 1
fi

# Start the development server
echo "⚛️  Starting React development server on http://localhost:3000"
npm run dev