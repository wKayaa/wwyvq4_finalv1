#!/bin/bash
# Setup script for AIO Exploit Framework
# Author: wKayaa
# Date: 2025-06-24 17:02:05 UTC

set -e

echo "🚀 AIO Exploit Framework Setup Script"
echo "======================================"

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not installed"
    exit 1
}

# Check pip
echo "📦 Checking pip..."
pip3 --version || {
    echo "❌ pip3 is required but not installed"
    exit 1
}

# Install dependencies
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Installing core dependencies..."
    pip3 install -r requirements.txt --user --timeout 30 || {
        echo "⚠️ Some dependencies failed to install, but framework may still work"
        echo "You can manually install missing packages as needed"
    }
    echo "✅ Dependencies installation completed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p exports
mkdir -p uploads
mkdir -p static/{css,js}
echo "✅ Directories created"

# Create default config if it doesn't exist
echo "⚙️ Setting up configuration..."
if [ ! -f "framework_config.yaml" ]; then
    cat > framework_config.yaml << EOF
performance:
  max_threads: 500
  timeout_per_operation: 10
  max_concurrent_clusters: 100

integrations:
  telegram_enabled: false
  telegram_token: ""
  telegram_chat_id: ""
  web_interface_enabled: false
  api_server_enabled: false

network:
  web_interface_port: 5000
  api_server_port: 8080
  bind_address: "0.0.0.0"

logging:
  level: "INFO"
  file: "framework.log"
  console: true

exploitation:
  mode: "aggressive"
  scan_only: false
  mail_focus: false
EOF
    echo "✅ Default configuration created"
else
    echo "⚠️ Configuration file already exists"
fi

# Test framework imports
echo "🧪 Testing framework..."
python3 -c "from framework import ModularOrchestrator, WebInterface, APIServer; print('✅ Framework imports successful')" || {
    echo "❌ Framework test failed"
    exit 1
}

# Test launcher
echo "🧪 Testing launcher..."
python3 launcher.py --help > /dev/null || {
    echo "❌ Launcher test failed"
    exit 1
}

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Quick Start:"
echo "   # Basic exploitation:"
echo "   python3 launcher.py --mode exploit --file targets_massive_optimized.txt"
echo ""
echo "   # With web interface:"
echo "   python3 launcher.py --web --api --mode scan"
echo ""
echo "   # With Telegram notifications:"
echo "   python3 launcher.py --telegram-token YOUR_TOKEN --telegram-chat YOUR_CHAT_ID"
echo ""
echo "🌐 Web interface will be available at: http://localhost:5000"
echo "🔌 API server will be available at: http://localhost:8080"
echo ""
echo "📖 Check README for more usage examples"