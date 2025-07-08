#!/usr/bin/env python3
"""
🎯 WWYVQ Credential Hunter Demo
Demonstrates the complete system with exact formatting as per requirements
Author: wKayaa | 2025
"""

import asyncio
import json
from datetime import datetime
from cracker_telegram_notifier import CrackerTelegramNotifier, TelegramConfig
from enhanced_credential_validator import EnhancedCredentialValidator, CredentialValidationResult
from realtime_stats_manager import stats_manager

async def demo_cracker_notifications():
    """Demo the exact cracker-style notifications"""
    print("🚀 WWYVQ Credential Hunter Demo")
    print("=" * 50)
    
    # Create a demo config (disabled for demo)
    config = TelegramConfig(
        bot_token='demo_token',
        chat_id='demo_chat',
        enabled=False  # Disable actual sending for demo
    )
    
    async with CrackerTelegramNotifier(config) as notifier:
        notifier.set_crack_info('#7849', 'wKayaa')
        
        # Demo SendGrid hit
        print("\n📧 SendGrid Hit Example:")
        print("-" * 40)
        
        sendgrid_result = CredentialValidationResult(
            service='SendGrid',
            credential_type='sendgrid_key',
            value='SG.v7A0566sRcKgwNbbN_M6ZA.zPIPOIUw7849a1b2c3d4e5f6789012345678901234567890123456789012345',
            is_valid=True,
            validation_method='SENDGRID_API_VERIFICATION',
            permissions=['mail.send', 'verified_senders'],
            quota_info={'credits': 'unlimited', 'senders': ['support@company.com', 'noreply@company.com']},
            validated_at=datetime.utcnow().isoformat(),
            confidence_score=98.0
        )
        
        # Generate the exact format
        hit_id = f"#425{notifier.hit_counter + 1:04d}"
        cred_preview = "SG.v7A0566sRcKgwNbbN_M6ZA.zPIPOIUw..."
        
        message = f"""✨ New Hit ({hit_id})

🔑 KEY:
{cred_preview}

💳 Credits: unlimited
🎯 Type: sendgrid
📧 Senders: ['support@company.com', 'noreply@company.com']
🔒 HardLimit: true

🔥 HIT WORKS: Yes

🌐 URL: https://example.com/api/config
🆔 Crack ID: #7849"""
        
        print(message)
        
        # Demo AWS hit
        print("\n🟠 AWS Hit Example:")
        print("-" * 40)
        
        aws_result = CredentialValidationResult(
            service='AWS',
            credential_type='aws_access_key',
            value='AKIA1234567890123456',
            is_valid=True,
            validation_method='AWS_STS_VALIDATION',
            permissions=['ses:SendEmail', 'ses:GetSendQuota'],
            quota_info={'daily_limit': 'unlimited', 'remaining': 'unlimited'},
            validated_at=datetime.utcnow().isoformat(),
            confidence_score=95.0
        )
        
        hit_id = f"#425{notifier.hit_counter + 2:04d}"
        cred_preview = "AKIA123456..."
        
        message = f"""✨ New Hit ({hit_id})

🔑 KEY:
{cred_preview}

💳 Credits: unlimited
🎯 Type: aws
📧 Senders: [SES verified]
🔒 HardLimit: false

🔥 HIT WORKS: Yes

🌐 URL: https://api.cloud.com/credentials
🆔 Crack ID: #7849"""
        
        print(message)
        
        # Demo statistics
        print("\n📊 Real-time Statistics Example:")
        print("-" * 40)
        
        now = datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
        
        stats_message = f"""📊 Crack "wKayaa" (#7849) stats:
⏰ Last Updated: {now}
⏱️ Timeout: 17
🔄 Threads: 100000
🎯 Status: running
🎯 Hits: 2
📂 Checked Paths: 1250
🔗 Checked URLs: 2487
❌ Invalid URLs: 1637
📊 Total URLs: 4124/42925357
⏳ Progression: 0.01%
🕐 ETA: 02d 17h 52m 27s"""
        
        print(stats_message)

async def demo_real_validation():
    """Demo real credential validation"""
    print("\n🔍 Real Credential Validation Demo:")
    print("=" * 50)
    
    async with EnhancedCredentialValidator() as validator:
        # Test various credential types
        test_credentials = [
            {
                'type': 'sendgrid_key',
                'value': 'SG.v7A0566sRcKgwNbbN_M6ZA.zPIPOIUw7849a1b2c3d4e5f6789012345678901234567890123456789012345',
                'service': 'SendGrid',
                'extracted_at': datetime.utcnow().isoformat(),
                'confidence': 85.0
            },
            {
                'type': 'aws_access_key',
                'value': 'AKIA1234567890123456',
                'service': 'AWS',
                'extracted_at': datetime.utcnow().isoformat(),
                'confidence': 80.0
            },
            {
                'type': 'mailgun_key',
                'value': 'key-12345678901234567890123456789012',
                'service': 'Mailgun',
                'extracted_at': datetime.utcnow().isoformat(),
                'confidence': 75.0
            }
        ]
        
        print(f"📋 Testing {len(test_credentials)} credentials...")
        
        results = await validator.validate_credentials(test_credentials)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.service} {result.credential_type}:")
            print(f"   ✅ Valid: {result.is_valid}")
            print(f"   🔍 Method: {result.validation_method}")
            print(f"   📊 Confidence: {result.confidence_score:.1f}%")
            print(f"   🔑 Permissions: {', '.join(result.permissions) if result.permissions else 'None'}")
            
            if result.quota_info:
                print(f"   💳 Quota: {result.quota_info}")
            
            if result.error_message:
                print(f"   ❌ Error: {result.error_message}")

async def demo_stats_manager():
    """Demo the real-time stats manager"""
    print("\n📊 Real-time Stats Manager Demo:")
    print("=" * 50)
    
    # Create a demo session
    session = stats_manager.create_session(
        "demo_session",
        "wKayaa",
        "#7849",
        ["target1.com", "target2.com", "target3.com"]
    )
    
    print(f"📝 Created session: {session.session_id}")
    
    # Simulate some activity
    for i in range(5):
        stats_manager.record_url_check(session.session_id, f"https://target{i}.com/api", True)
        stats_manager.record_path_check(session.session_id, f"/config/{i}")
    
    # Record some hits
    stats_manager.record_hit(session.session_id, "sendgrid_key", "SendGrid")
    stats_manager.record_hit(session.session_id, "aws_access_key", "AWS")
    
    # Get current stats
    session_stats = stats_manager.get_session_stats(session.session_id)
    
    print(f"\n📈 Current Session Stats:")
    for key, value in session_stats.items():
        print(f"   {key}: {value}")
    
    # Get global stats
    global_stats = stats_manager.get_global_stats()
    print(f"\n🌍 Global Stats:")
    for key, value in global_stats.items():
        print(f"   {key}: {value}")

async def main():
    """Main demo function"""
    print("🎯 WWYVQ CREDENTIAL HUNTER - COMPLETE DEMO")
    print("=" * 60)
    
    try:
        await demo_cracker_notifications()
        await demo_real_validation()
        await demo_stats_manager()
        
        print("\n✅ Demo completed successfully!")
        print("\nTo use the system:")
        print("1. Update wwyvq_config.json with your Telegram bot credentials")
        print("2. Create a targets.txt file with your targets")
        print("3. Run: python wwyvq_credential_hunter.py --targets targets.txt")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())