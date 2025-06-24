# AIO Exploit Framework - Quick Start Guide

## Overview
The AIO Exploit Framework has been restructured with a proper modular architecture. The main entry point is `launcher.py` which uses the new `framework/` module.

## Installation

### Quick Setup
```bash
# Run the setup script
./setup_framework.sh
```

### Manual Installation
```bash
# Install dependencies
pip3 install -r requirements.txt --user

# Test framework
python3 test_framework.py
```

## Usage

### Basic Commands

**Exploitation with targets file:**
```bash
python3 launcher.py --targets targets_massive_optimized.txt --mode exploit
```

**With Telegram notifications:**
```bash
python3 launcher.py --targets targets_massive_optimized.txt \
  --telegram-token "YOUR_TOKEN" \
  --telegram-chat "YOUR_CHAT_ID"
```

**With web interface and API:**
```bash
python3 launcher.py --web --api --mode scan
```

### Available Modes
- `scan` - Target scanning mode
- `exploit` - K8s exploitation mode (default)
- `mail` - Mail services hunting mode  
- `all` - Full exploitation pipeline

### Interface Access
- **Web Interface**: http://localhost:5000 (with --web flag)
- **API Server**: http://localhost:8080 (with --api flag)

## Framework Structure

```
framework/
├── __init__.py           # Main exports
├── orchestrator.py       # ModularOrchestrator - main coordination
├── web_interface.py      # WebInterface - Flask web UI
├── api_server.py         # APIServer - REST API
├── config.py            # ConfigManager - YAML configuration
└── utils.py             # FrameworkUtils - utilities
```

## Configuration

The framework uses `framework_config.yaml` for configuration:

```yaml
performance:
  max_threads: 500
  timeout_per_operation: 10
  max_concurrent_clusters: 100

integrations:
  telegram_enabled: false
  telegram_token: ""
  telegram_chat_id: ""

network:
  web_interface_port: 5000
  api_server_port: 8080
  bind_address: "0.0.0.0"

exploitation:
  mode: "aggressive"
  scan_only: false
  mail_focus: false
```

## API Endpoints

When running with `--api`, the following endpoints are available:

- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Framework status
- `GET /config` - Current configuration
- `POST /config` - Update configuration
- `POST /exploit/k8s` - Start K8s exploitation
- `POST /exploit/mail` - Start mail hunting
- `POST /exploit/full` - Start full exploitation
- `POST /targets/load` - Load targets from file
- `GET /targets/expand` - Expand CIDR targets

### Example API Usage
```bash
# Check health
curl http://localhost:8080/health

# Start exploitation
curl -X POST http://localhost:8080/exploit/k8s \
  -H "Content-Type: application/json" \
  -d '{"targets": ["127.0.0.1", "localhost"]}'
```

## Integration with Existing Modules

The framework integrates existing modules:
- `kubernetes_advanced.py` - K8s orchestrator
- `k8s_exploit_master.py` - Exploit master
- `mail_services_hunter.py` - Mail hunting
- `telegram_perfect_hits.py` - Telegram notifications
- `app.py` - Web interface

## Troubleshooting

### ModuleNotFoundError
If you see import errors, make sure dependencies are installed:
```bash
pip3 install -r requirements.txt --user
```

### Web Interface Issues
The framework creates a minimal web interface if the full Flask app is not available. Install flask-socketio for full functionality:
```bash
pip3 install flask-socketio --user
```

### Testing
Run the test suite to validate everything works:
```bash
python3 test_framework.py
```

## Backwards Compatibility

All existing scripts continue to work:
- `kubernetes_advanced.py`
- `k8s_exploit_master.py`
- `wwyvq_master_final.py`
- etc.

The framework provides a unified interface while maintaining compatibility with existing tools.