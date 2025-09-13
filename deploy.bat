@echo off
REM COI Document Extraction Platform - Windows Deployment Script
REM This script helps deploy the application to production

echo 🚀 Deploying COI Document Extraction Platform...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python installation found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check for required environment variables
echo 🔍 Checking environment configuration...
if not exist ".env" (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # OpenAI Configuration
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Flask Configuration
        echo FLASK_ENV=production
        echo FLASK_DEBUG=False
        echo.
        echo # Add your configuration here
    ) > .env
    echo 📝 Please edit .env file with your actual API keys and configuration.
)

REM Check for Google Vision API credentials
if not exist "config\google_ocr.json" (
    echo ⚠️  Google Vision API credentials not found.
    echo 📝 Please place your Google service account JSON file at config\google_ocr.json
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "extracted_json" mkdir extracted_json
if not exist "logs" mkdir logs

echo ✅ Deployment preparation complete!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Add Google Vision API credentials to config\google_ocr.json
echo 3. Run: python app.py
echo 4. Access the application at http://localhost:5000
echo.
echo 🔧 For production deployment:
echo - Use a WSGI server like Gunicorn
echo - Set up a reverse proxy with Nginx
echo - Configure SSL certificates
echo - Set up monitoring and logging
echo.
pause
