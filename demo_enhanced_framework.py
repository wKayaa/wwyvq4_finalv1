#!/usr/bin/env python3
"""
🎯 WWYVQ Enhanced Framework Demo
Demonstrates the new functionality without needing real credentials
"""

import asyncio
import json
import os
from datetime import datetime
from enhanced_credential_validator import EnhancedCredentialValidator, CredentialValidationResult
from professional_telegram_notifier import ProfessionalTelegramNotifier, TelegramConfig
from organized_results_manager import OrganizedResultsManager

async def demo_credential_validation():
    """Demo credential validation functionality"""
    print("🔍 DEMO: Credential Validation")
    print("=" * 50)
    
    # Create sample credentials for testing
    test_content = """
    {
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "sendgrid_api_key": "SG.demo_key_for_testing_only.example123456789",
        "mailgun_api_key": "key-12345678901234567890123456789012",
        "real_looking_aws_key": "AKIA1234567890123456",
        "real_looking_secret": "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890abcd"
    }
    """
    
    # Initialize validator
    async with EnhancedCredentialValidator() as validator:
        print("✅ Credential validator initialized")
        
        # Extract credentials
        credentials = validator.extract_credentials(test_content, "demo://test")
        print(f"📊 Extracted {len(credentials)} credentials")
        
        # Validate credentials
        validation_results = await validator.validate_credentials(credentials)
        print(f"🔍 Validated {len(validation_results)} credentials")
        
        # Display results
        for i, result in enumerate(validation_results, 1):
            print(f"\n📋 Result #{i}:")
            print(f"  Service: {result.service}")
            print(f"  Type: {result.credential_type}")
            print(f"  Valid: {result.is_valid}")
            print(f"  Confidence: {result.confidence_score:.1f}%")
            print(f"  Method: {result.validation_method}")
            if result.error_message:
                print(f"  Error: {result.error_message}")

def demo_organized_results():
    """Demo organized results management"""
    print("\n📁 DEMO: Organized Results Management")
    print("=" * 50)
    
    # Initialize results manager
    results_manager = OrganizedResultsManager()
    print(f"✅ Results manager initialized")
    print(f"📂 Session directory: {results_manager.session_dir}")
    
    # Create sample validation results
    sample_results = [
        CredentialValidationResult(
            service="AWS",
            credential_type="aws_access_key",
            value="AKIA1234567890123456",
            is_valid=True,
            validation_method="FORMAT_CHECK",
            permissions=["ses:SendEmail"],
            quota_info={"daily_limit": "Unknown"},
            validated_at=datetime.utcnow().isoformat(),
            confidence_score=85.0
        ),
        CredentialValidationResult(
            service="SendGrid",
            credential_type="sendgrid_key",
            value="SG.demo_key_for_testing_only.example123456789",
            is_valid=False,
            validation_method="API_TEST",
            permissions=[],
            quota_info={},
            error_message="Test key detected",
            validated_at=datetime.utcnow().isoformat(),
            confidence_score=20.0
        ),
        CredentialValidationResult(
            service="Mailgun",
            credential_type="mailgun_key",
            value="key-12345678901234567890123456789012",
            is_valid=True,
            validation_method="FORMAT_CHECK",
            permissions=["messages:send"],
            quota_info={"service": "mailgun"},
            validated_at=datetime.utcnow().isoformat(),
            confidence_score=80.0
        )
    ]
    
    # Save results
    for result in sample_results:
        results_manager.save_credential(result)
        print(f"💾 Saved {result.service} credential")
    
    # Generate summary
    summary = results_manager.generate_session_summary()
    print(f"\n📊 Session Summary:")
    print(f"  Total credentials: {summary['total_credentials']}")
    print(f"  Valid credentials: {summary['valid_credentials']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")
    print(f"  Services found: {list(summary['services_found'].keys())}")
    
    # Show file structure
    print(f"\n📁 Generated Files:")
    for file in results_manager.session_dir.rglob('*.txt'):
        print(f"  {file.relative_to(results_manager.session_dir)}")

def demo_telegram_notifications():
    """Demo Telegram notifications (without actually sending)"""
    print("\n📡 DEMO: Professional Telegram Notifications")
    print("=" * 50)
    
    # Create config (won't actually send)
    config = TelegramConfig(
        bot_token="demo_token",
        chat_id="demo_chat_id",
        enabled=False  # Disabled for demo
    )
    
    # Initialize notifier
    notifier = ProfessionalTelegramNotifier(config)
    print("✅ Telegram notifier initialized (demo mode)")
    
    # Create sample validation result
    sample_result = CredentialValidationResult(
        service="AWS",
        credential_type="aws_access_key",
        value="AKIA1234567890123456",
        is_valid=True,
        validation_method="FORMAT_CHECK",
        permissions=["ses:SendEmail", "sns:Publish"],
        quota_info={"daily_limit": "1000", "account_type": "standard"},
        validated_at=datetime.utcnow().isoformat(),
        confidence_score=95.0
    )
    
    # Show what the notification would look like
    print("\n📨 Sample Notification Format:")
    print("-" * 30)
    
    sample_message = f"""🚨 **WWYVQ CREDENTIAL ALERT** 🚨

✅ **STATUS**: VALID
🟠 **SERVICE**: {sample_result.service}
🔑 **TYPE**: {sample_result.credential_type}
📊 **CONFIDENCE**: {sample_result.confidence_score:.1f}%
🕐 **VALIDATED**: {sample_result.validated_at[:19]}Z

**📋 CREDENTIAL DETAILS:**
├── Value: `{sample_result.value}`
├── Method: {sample_result.validation_method}
├── Permissions: {', '.join(sample_result.permissions)}
└── Quota Info: {json.dumps(sample_result.quota_info, indent=2)}

**🎯 HIT ANALYSIS:**
├── Hit ID: #1
├── Session Time: 00h 00m 05s
├── Threat Level: 🔥 CRITICAL
└── Exploitation Ready: YES

**👨‍💻 OPERATOR: wKayaa**
**🚀 FRAMEWORK: WWYVQ v5.0**

#WWYVQ #CredentialHunting #SecurityTesting #wKayaa"""
    
    print(sample_message)

def show_file_structure():
    """Show the organized file structure"""
    print("\n🏗️  ENHANCED FRAMEWORK STRUCTURE")
    print("=" * 50)
    
    print("📁 Main Directory:")
    main_files = [
        "wwyvq_enhanced_framework.py",
        "enhanced_credential_validator.py", 
        "professional_telegram_notifier.py",
        "organized_results_manager.py",
        "wwyvq_config.json",
        "test_targets.txt"
    ]
    
    for file in main_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print("\n📁 Archive Directory:")
    if os.path.exists("archive"):
        archived_files = os.listdir("archive")
        print(f"  📊 {len(archived_files)} files archived")
        for file in sorted(archived_files)[:5]:  # Show first 5
            print(f"    {file}")
        if len(archived_files) > 5:
            print(f"    ... and {len(archived_files) - 5} more files")
    
    print("\n📁 Results Directory:")
    if os.path.exists("results"):
        results_sessions = [d for d in os.listdir("results") if os.path.isdir(os.path.join("results", d))]
        print(f"  📊 {len(results_sessions)} session(s) available")
        for session in sorted(results_sessions)[-3:]:  # Show last 3
            print(f"    📂 {session}")

async def main():
    """Main demo function"""
    print("🚀 WWYVQ ENHANCED FRAMEWORK DEMO")
    print("=" * 80)
    print("This demo showcases the new professional features:")
    print("✅ Enhanced credential validation")
    print("✅ Professional Telegram notifications")
    print("✅ Organized results management")
    print("✅ Clean repository structure")
    print("=" * 80)
    
    # Run demos
    await demo_credential_validation()
    demo_organized_results()
    demo_telegram_notifications()
    show_file_structure()
    
    print("\n🎉 DEMO COMPLETE!")
    print("=" * 50)
    print("🔧 To use the real framework:")
    print("  1. Edit wwyvq_config.json with your Telegram credentials")
    print("  2. Add real targets to test_targets.txt")
    print("  3. Run: python3 wwyvq_enhanced_framework.py --targets test_targets.txt --config wwyvq_config.json")
    print("\n👨‍💻 Author: wKayaa | WWYVQ Enhanced Framework v5.0")

if __name__ == "__main__":
    asyncio.run(main())