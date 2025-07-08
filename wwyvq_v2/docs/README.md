# WWYVQ Framework v2 - Complete Documentation

## Overview

WWYVQ Framework v2 is a completely refactored, modular Kubernetes security framework designed for professional penetration testing and security assessment. The new architecture provides advanced features, better organization, and improved extensibility.

## 🏗️ Architecture

### Core Components

```
wwyvq_v2/
├── core/                    # 🧠 Central Engine
│   ├── engine.py           # Main orchestration engine
│   ├── config.py           # Configuration management
│   ├── session.py          # Session management with persistence
│   ├── target.py           # Target management with CIDR expansion
│   └── logger.py           # Professional logging system
│
├── modules/                 # 🔧 Specialized Modules
│   ├── exploit/            # Kubernetes exploitation
│   │   └── k8s_scanner.py  # Cluster detection and reconnaissance
│   ├── validator/          # Credential validation
│   │   └── credential_validator.py  # Multi-service validation
│   ├── notifier/           # Real-time notifications
│   │   └── telegram.py     # Telegram notifications
│   ├── exporter/           # Results management
│   │   └── results_organizer.py  # Export and organization
│   ├── scanner/            # Network scanning modules
│   └── utils/              # Utility functions
│
├── interfaces/             # 🖥️ User Interfaces
│   ├── cli/               # Command-line interface
│   │   └── main.py        # Advanced CLI with colors
│   ├── web/               # Web dashboard (planned)
│   └── api/               # REST API (planned)
│
├── configs/               # ⚙️ Configuration Files
│   ├── default.yaml       # Default configuration
│   └── production.yaml    # Production settings
│
└── wwyvq.py              # 🚀 Main entry point
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/wKayaa/wwyvq4_finalv1.git
cd wwyvq4_finalv1

# Install dependencies
pip install aiohttp pyyaml

# Verify installation
python wwyvq.py --help
```

### Basic Usage

```bash
# Basic scan
python wwyvq.py scan --targets targets.txt

# Advanced scan with custom settings
python wwyvq.py scan --targets "192.168.1.0/24" --mode aggressive --concurrent 200

# Configuration management
python wwyvq.py config --show
python wwyvq.py config --profile production

# Safe mode (recommended for production environments)
python wwyvq.py scan --targets targets.txt --safe-mode
```

## 🔧 Core Features

### 1. Unified Engine

The central engine (`WWYVQEngine`) orchestrates all operations:

- **Operation Management**: Manages scan, exploit, and validation operations
- **Module Loading**: Dynamic loading of specialized modules
- **Session Persistence**: Automatic session management with recovery
- **Concurrency Control**: Intelligent handling of parallel operations

### 2. Configuration Management

Advanced configuration system with:

- **Profile Support**: Multiple configuration profiles (dev, prod, test)
- **YAML/JSON Support**: Flexible configuration formats
- **Hot Reload**: Runtime configuration updates
- **Validation**: Automatic configuration validation

### 3. Session Management

Professional session handling:

- **Persistence**: Sessions survive application restarts
- **Recovery**: Automatic recovery from interruptions
- **Cleanup**: Automatic cleanup of expired sessions
- **Export**: Complete session export capability

### 4. Target Management

Intelligent target processing:

- **CIDR Expansion**: Automatic CIDR range expansion
- **DNS Resolution**: Hostname to IP resolution
- **Validation**: Target validation and filtering
- **Exclusions**: Configurable target exclusions

### 5. Professional Logging

Advanced logging system:

- **Structured Logging**: Consistent log format across modules
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File Rotation**: Automatic log file rotation
- **Search**: Built-in log search capabilities

## 📦 Modules

### Kubernetes Scanner (`modules/exploit/k8s_scanner.py`)

Advanced Kubernetes cluster detection:

```python
from wwyvq_v2.modules.exploit.k8s_scanner import KubernetesScanner

scanner = KubernetesScanner(config_manager, logger)
clusters = await scanner.scan_target("192.168.1.100")
```

**Features:**
- Multi-protocol scanning (HTTP/HTTPS)
- Version detection
- Vulnerability assessment
- Service enumeration
- SSL/TLS support

### Credential Validator (`modules/validator/credential_validator.py`)

Multi-service credential validation:

```python
from wwyvq_v2.modules.validator.credential_validator import CredentialValidator, Credential

validator = CredentialValidator(config_manager, logger)
credential = Credential(
    service="kubernetes",
    endpoint="https://cluster.example.com:6443",
    token="eyJhbGciOi..."
)
result = await validator.validate_credential(credential)
```

**Supported Services:**
- Kubernetes API
- AWS (STS validation)
- Azure (Management API)
- Google Cloud Platform
- Docker Registry
- Database connections
- Email services (SMTP/IMAP/POP3)
- Generic HTTP services

### Telegram Notifier (`modules/notifier/telegram.py`)

Professional Telegram notifications:

```python
from wwyvq_v2.modules.notifier.telegram import TelegramNotifier

notifier = TelegramNotifier(config_manager, logger)
await notifier.send_perfect_hit(
    service="kubernetes",
    endpoint="https://cluster.local:6443",
    credentials={"token": "valid_token"}
)
```

**Notification Types:**
- Operation start/complete
- Perfect hits (valid credentials)
- Critical alerts
- Error notifications
- Statistics summaries

### Results Organizer (`modules/exporter/results_organizer.py`)

Advanced results management:

```python
from wwyvq_v2.modules.exporter.results_organizer import ResultsOrganizer, ExportOptions

organizer = ResultsOrganizer(config_manager, logger)
export_options = ExportOptions(format_type="json", mask_credentials=True)
files = organizer.export_results(export_options)
```

**Export Formats:**
- JSON (structured data)
- CSV (tabular data)
- HTML (reports)
- XML (structured data)
- Compressed archives

## 🎯 Command Line Interface

### Available Commands

#### Scan Command
```bash
python wwyvq.py scan --targets targets.txt [OPTIONS]

Options:
  --mode {passive,standard,aggressive}  Scan mode (default: standard)
  --concurrent INTEGER                  Concurrent connections (default: 100)
  --timeout INTEGER                     Timeout per target (default: 30)
  --output FILE                        Output file path
```

#### Exploit Command
```bash
python wwyvq.py exploit --targets targets.txt [OPTIONS]

Options:
  --mode {passive,standard,aggressive}  Exploit mode (default: standard)
  --concurrent INTEGER                  Concurrent connections (default: 50)
  --stealth                            Enable stealth mode
  --no-deploy                          Disable pod deployment
  --output DIRECTORY                   Output directory
```

#### Validate Command
```bash
python wwyvq.py validate --credentials creds.json [OPTIONS]

Options:
  --services TEXT                      Services to validate
  --concurrent INTEGER                 Concurrent validations (default: 10)
  --output FILE                       Output file path
```

#### Config Command
```bash
python wwyvq.py config [OPTIONS]

Options:
  --profile TEXT                       Load configuration profile
  --create-profile TEXT               Create new profile
  --show                              Show current configuration
  --validate                          Validate configuration
  --reset                             Reset to defaults
```

### Global Options
```bash
Global Options:
  --config FILE                        Configuration file path
  --log-level {DEBUG,INFO,WARNING,ERROR}  Log level (default: INFO)
  --session-id TEXT                    Session ID to restore
  --safe-mode                          Enable safe mode
  --version                            Show version information
```

## ⚙️ Configuration

### Default Configuration (`configs/default.yaml`)

```yaml
version: "2.0.0"

core:
  session_id: "auto"
  max_concurrent: 100
  timeout: 30
  retry_attempts: 3
  safe_mode: true
  debug_mode: false

modules:
  exploit:
    enabled: true
    stealth_mode: false
    max_pods: 10
  
  validator:
    enabled: true
    api_timeout: 10
    max_retries: 3
  
  notifier:
    telegram:
      enabled: false
      token: ""
      chat_id: ""

targets:
  cidr_expansion: true
  max_ips_per_cidr: 1000
  default_ports: [6443, 8443, 8080]

logging:
  level: "INFO"
  file_enabled: true
  file_path: "logs/wwyvq.log"
  console_enabled: true

security:
  encryption_enabled: true
  audit_logging: true
  session_timeout: 3600
  safe_mode_restrictions:
    - "no_pod_deployment"
    - "readonly_operations"
```

### Production Configuration (`configs/production.yaml`)

Production settings with enhanced capabilities:

```yaml
core:
  max_concurrent: 500
  safe_mode: false

modules:
  exploit:
    stealth_mode: true
    max_pods: 50
  
  notifier:
    telegram:
      enabled: true
      token: "${TELEGRAM_TOKEN}"
      chat_id: "${TELEGRAM_CHAT_ID}"

targets:
  max_ips_per_cidr: 10000

security:
  safe_mode_restrictions: []  # No restrictions in production
```

## 🛡️ Security Features

### Safe Mode

Safe mode provides additional security restrictions:

- **No Pod Deployment**: Prevents deployment of malicious pods
- **Read-Only Operations**: Limits operations to read-only
- **No Privilege Escalation**: Prevents privilege escalation attempts
- **Network Restrictions**: Limits network operations

### Audit Logging

Comprehensive audit trail:

- All operations logged with timestamps
- User actions tracked
- Configuration changes recorded
- Security events highlighted

### Credential Protection

Advanced credential handling:

- **Encryption at Rest**: Credentials encrypted when stored
- **Memory Protection**: Secure memory handling
- **Masking**: Automatic credential masking in logs
- **Secure Export**: Safe credential export options

## 📊 Session Management

### Creating Sessions

Sessions are automatically created and managed:

```python
# Automatic session creation
engine = WWYVQEngine()
await engine.initialize()

# Manual session creation with metadata
session_id = await engine.session_manager.create_session({
    "user": "analyst",
    "purpose": "vulnerability_assessment",
    "environment": "production"
})
```

### Session Persistence

Sessions persist across application restarts:

- **Automatic Recovery**: Sessions automatically restored
- **State Preservation**: All operation state maintained
- **Results Retention**: Results preserved across sessions

### Session Export

Complete session export capability:

```bash
# Export session data
python wwyvq.py session export --session-id abc123 --format json
```

## 🔍 Target Processing

### CIDR Expansion

Automatic CIDR range processing:

```python
# Automatic expansion
targets = ["192.168.1.0/24", "10.0.0.0/8"]
processed = await target_manager.process_targets(targets)
```

### Target Validation

Intelligent target validation:

- **IP Validation**: RFC-compliant IP validation
- **Port Validation**: Valid port range checking
- **Exclusion Lists**: Configurable target exclusions
- **Safe Mode Filtering**: Additional filtering in safe mode

## 📈 Performance

### Concurrency Control

Intelligent concurrency management:

- **Adaptive Limits**: Automatic concurrency adjustment
- **Resource Monitoring**: CPU and memory monitoring
- **Rate Limiting**: Intelligent rate limiting
- **Connection Pooling**: Efficient connection reuse

### Memory Management

Optimized memory usage:

- **Streaming Processing**: Large dataset streaming
- **Memory Cleanup**: Automatic memory cleanup
- **Resource Limits**: Configurable resource limits

## 🧪 Testing

### Architecture Validation

```bash
# Run architecture tests
python test_architecture.py
```

### Comprehensive Demo

```bash
# Run comprehensive demo
python demo_wwyvq_v2.py
```

### Individual Module Testing

```python
# Test individual modules
from wwyvq_v2.modules.exploit.k8s_scanner import KubernetesScanner

scanner = KubernetesScanner(config_manager, logger)
stats = scanner.get_statistics()
```

## 🚀 Advanced Usage

### Custom Module Development

Create custom modules following the framework pattern:

```python
class CustomModule:
    def __init__(self, config_manager, logger):
        self.config_manager = config_manager
        self.logger = logger
    
    async def custom_operation(self, targets):
        # Module implementation
        pass
```

### API Integration

Integrate with the framework programmatically:

```python
from wwyvq_v2.core import WWYVQEngine
from wwyvq_v2.core.engine import ExecutionMode

engine = WWYVQEngine()
await engine.initialize()

result = await engine.execute_operation(
    operation_type='scan',
    targets=['192.168.1.0/24'],
    mode=ExecutionMode.AGGRESSIVE
)
```

## 📚 Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes following the architecture patterns
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow Python PEP 8 guidelines
- Use type hints throughout
- Document all public functions
- Write comprehensive tests

## 🐛 Troubleshooting

### Common Issues

**Module Loading Errors**
```bash
# Check module dependencies
python -c "import aiohttp, yaml; print('Dependencies OK')"
```

**Configuration Issues**
```bash
# Validate configuration
python wwyvq.py config --validate
```

**Permission Errors**
```bash
# Run with proper permissions
sudo python wwyvq.py scan --targets targets.txt
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python wwyvq.py scan --targets targets.txt --log-level DEBUG
```

## 📞 Support

For support and questions:

- **Documentation**: Check this comprehensive guide
- **Issues**: Create GitHub issues for bugs
- **Security**: Report security issues privately

## 🎉 Conclusion

WWYVQ Framework v2 represents a complete architectural overhaul, providing a professional, modular, and extensible platform for Kubernetes security assessment. The new design ensures scalability, maintainability, and ease of use while providing powerful capabilities for security professionals.

The framework is production-ready and suitable for professional penetration testing engagements, security research, and educational purposes.