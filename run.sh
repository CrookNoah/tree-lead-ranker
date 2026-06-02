#!/bin/bash

# Tree Lead Ranker - Quick Start Script

echo "🌲 Tree Lead Ranker"
echo "===================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "🔑 Please edit .env and add your API keys:"
    echo "   - GOOGLE_PLACES_API_KEY"
    echo "   - ANTHROPIC_API_KEY (or OPENAI_API_KEY)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if API keys are set
if grep -q "your_google_places_api_key_here" .env; then
    echo ""
    echo "❌ API keys not configured!"
    echo "📝 Edit .env and add:"
    echo "   - GOOGLE_PLACES_API_KEY"
    echo "   - ANTHROPIC_API_KEY (or OPENAI_API_KEY)"
    exit 1
fi

echo "✅ Configuration complete"
echo ""
echo "🚀 Starting server..."
echo "   API: http://localhost:8000"
echo "   Dashboard: http://localhost:8000/docs (or open dashboard.html)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python main.py
