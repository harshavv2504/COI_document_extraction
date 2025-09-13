#!/bin/bash

# COI Document Extraction Platform - Deployment Script
# This script helps deploy the application to production

echo "🚀 Deploying COI Document Extraction Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for required environment variables
echo "🔍 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Add your configuration here
EOF
    echo "📝 Please edit .env file with your actual API keys and configuration."
fi

# Check for Google Vision API credentials
if [ ! -f "config/google_ocr.json" ]; then
    echo "⚠️  Google Vision API credentials not found."
    echo "📝 Please place your Google service account JSON file at config/google_ocr.json"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p extracted_json
mkdir -p logs

# Set permissions
echo "🔐 Setting file permissions..."
chmod +x app.py
chmod 755 uploads
chmod 755 extracted_json

echo "✅ Deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Add Google Vision API credentials to config/google_ocr.json"
echo "3. Run: python app.py"
echo "4. Access the application at http://localhost:5000"
echo ""
echo "🔧 For production deployment:"
echo "- Use a WSGI server like Gunicorn"
echo "- Set up a reverse proxy with Nginx"
echo "- Configure SSL certificates"
echo "- Set up monitoring and logging"
