# 🔔 Simple Telegram Notifier for WWYVQ

This simple Telegram notifier has been added to the WWYVQ framework to send basic hit notifications.

## Features

- **Simple hit notifications**: Sends formatted alerts when credentials are found
- **Session tracking**: Start and completion notifications
- **Secure credential display**: Credentials are redacted in messages
- **Environment variable support**: Can be configured via environment variables or config file
- **Lightweight**: Minimal dependencies and straightforward implementation

## Configuration

### Option 1: Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

### Option 2: Configuration File
Edit `telegram_config.json`:
```json
{
    "bot_token": "your_bot_token_here",
    "chat_id": "your_chat_id_here",
    "enabled": true
}
```

### Option 3: Command Line Arguments
```bash
python wwyvq_master_final.py --telegram-token YOUR_TOKEN --telegram-chat YOUR_CHAT_ID
```

## Usage Examples

```bash
# Basic usage with Telegram notifications
python wwyvq_master_final.py --mode aggressive --target example.com --telegram-token YOUR_TOKEN --telegram-chat YOUR_CHAT_ID

# Using environment variables
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id
python wwyvq_master_final.py --mode mail --file targets.txt

# All modes with Telegram notifications
python wwyvq_master_final.py --mode all --file targets.txt --telegram-token YOUR_TOKEN --telegram-chat YOUR_CHAT_ID
```

## Message Format

When a credential hit is detected, you'll receive a message like:

```
🎯 WWYVQ HIT DETECTED

📅 Date: 2025-07-07 23:42:37
🔗 Source: https://example.com/config.json
🔑 Type: AWS
📊 Value: AKIA12...CDEF

#WWYVQ #Hit #Credential
```

## Setup Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token
4. Add the bot to your channel/group or get your personal chat ID
5. Configure the notifier using one of the methods above

## Integration

The simple Telegram notifier is automatically integrated into the main WWYVQ framework and will:

- Send a notification when a scan session starts
- Send individual notifications for each credential hit found
- Send a summary notification when the scan session completes
- Respect rate limits to avoid Telegram API restrictions

## Files

- `telegram_notifier.py` - Main notifier implementation
- `telegram_config.json` - Configuration file template
- Integration is in `wwyvq_master_final.py`

## Dependencies

- `aiohttp` - For HTTP requests to Telegram API (auto-installed)

The notifier is designed to be simple, reliable, and non-intrusive to the main WWYVQ framework functionality.