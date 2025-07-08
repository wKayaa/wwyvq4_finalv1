#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Comprehensive Demo
Author: wKayaa
Date: 2025-01-15

Démonstration complète des nouvelles fonctionnalités du framework v2.
"""

import asyncio
import sys
from pathlib import Path

# Ajout du chemin vers le framework
sys.path.insert(0, str(Path(__file__).parent))

from wwyvq_v2.core import WWYVQEngine, ConfigurationManager
from wwyvq_v2.core.engine import ExecutionMode
from wwyvq_v2.modules.validator.credential_validator import CredentialValidator, Credential
from wwyvq_v2.modules.notifier.telegram import TelegramNotifier
from wwyvq_v2.modules.exporter.results_organizer import ResultsOrganizer, OperationResults, ExportOptions
from wwyvq_v2.modules.exploit.k8s_scanner import KubernetesScanner


async def demo_core_functionality():
    """Démonstration des fonctionnalités core"""
    print("🚀 WWYVQ Framework v2 - Comprehensive Demo")
    print("=" * 60)
    
    # 1. Initialisation du moteur
    print("\n1. 🔧 Core Engine Initialization")
    engine = WWYVQEngine("wwyvq_v2/configs/default.yaml")
    
    if not await engine.initialize():
        print("❌ Failed to initialize engine")
        return False
    
    print("✅ Engine initialized successfully")
    
    # 2. Création d'une session de démonstration
    print("\n2. 🎯 Session Management Demo")
    session = await engine.session_manager.create_session({
        "demo": True,
        "user": "demo_user",
        "purpose": "comprehensive_demo"
    })
    print(f"✅ Demo session created: {session}")
    
    # 3. Gestion des cibles
    print("\n3. 📍 Target Management Demo")
    demo_targets = [
        "127.0.0.1",
        "localhost:8080",
        "192.168.1.0/29",  # Petit CIDR pour demo
        "https://httpbin.org/status/200"
    ]
    
    processed_targets = await engine.target_manager.process_targets(demo_targets)
    print(f"✅ Processed {len(demo_targets)} targets → {len(processed_targets)} final targets")
    
    await engine.shutdown()
    return True


async def demo_credential_validator():
    """Démonstration du validateur de credentials"""
    print("\n4. 🔍 Credential Validator Demo")
    
    config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
    logger = config_manager.get_config()  # Using config as mock logger
    
    # Mock logger
    class MockLogger:
        def info(self, msg, **kwargs):
            print(f"   INFO: {msg}")
        def error(self, msg, **kwargs):
            print(f"   ERROR: {msg}")
        def warning(self, msg, **kwargs):
            print(f"   WARNING: {msg}")
    
    validator = CredentialValidator(config_manager, MockLogger())
    
    # Test credentials
    test_credentials = [
        Credential(
            service="kubernetes",
            endpoint="https://127.0.0.1:6443",
            token="demo-token",
            metadata={"test": True}
        ),
        Credential(
            service="aws",
            endpoint="https://sts.amazonaws.com",
            api_key="demo-key",
            metadata={"region": "us-east-1"}
        ),
        Credential(
            service="http",
            endpoint="https://httpbin.org/basic-auth/user/pass",
            username="user",
            password="pass"
        )
    ]
    
    print(f"   Testing {len(test_credentials)} credentials...")
    
    # Validation
    results = await validator.validate_multiple_credentials(test_credentials)
    
    # Statistiques
    stats = validator.get_validation_statistics()
    print(f"   ✅ Validation completed:")
    print(f"     • Total: {stats['total_validations']}")
    print(f"     • Valid: {stats['valid_credentials']}")
    print(f"     • Success Rate: {stats['success_rate']:.1f}%")
    
    return len(results) > 0


async def demo_telegram_notifier():
    """Démonstration du notificateur Telegram"""
    print("\n5. 📱 Telegram Notifier Demo")
    
    config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
    
    # Mock logger
    class MockLogger:
        def info(self, msg, **kwargs):
            print(f"   INFO: {msg}")
        def error(self, msg, **kwargs):
            print(f"   ERROR: {msg}")
        def warning(self, msg, **kwargs):
            print(f"   WARNING: {msg}")
    
    notifier = TelegramNotifier(config_manager, MockLogger())
    
    # Test de configuration
    print(f"   Telegram configured: {notifier.is_configured()}")
    
    if not notifier.is_configured():
        print("   ⚠️ Telegram not configured (expected for demo)")
        
        # Démonstration des fonctionnalités sans envoi réel
        print("   📋 Available notification methods:")
        print("     • send_operation_start()")
        print("     • send_operation_complete()")
        print("     • send_perfect_hit()")
        print("     • send_critical_alert()")
        print("     • send_statistics_summary()")
    
    # Statistiques
    stats = notifier.get_notification_statistics()
    print(f"   📊 Notification statistics:")
    print(f"     • Total messages: {stats['total_messages']}")
    print(f"     • Success rate: {stats['success_rate']:.1f}%")
    print(f"     • Enabled: {stats['enabled']}")
    
    return True


async def demo_results_organizer():
    """Démonstration de l'organisateur de résultats"""
    print("\n6. 📊 Results Organizer Demo")
    
    config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
    
    # Mock logger
    class MockLogger:
        def info(self, msg, **kwargs):
            print(f"   INFO: {msg}")
        def error(self, msg, **kwargs):
            print(f"   ERROR: {msg}")
    
    organizer = ResultsOrganizer(config_manager, MockLogger(), "/tmp/demo_results")
    
    # Création d'un répertoire de session
    session_dir = organizer.create_session_directory("demo_session")
    print(f"   ✅ Session directory: {session_dir}")
    
    # Création de résultats de démonstration
    from datetime import datetime
    demo_results = OperationResults(
        operation_id="demo_op_001",
        operation_type="scan",
        session_id="demo_session",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        results={
            "clusters_found": [
                {"endpoint": "127.0.0.1:6443", "version": "v1.21.0", "accessible": True},
                {"endpoint": "192.168.1.100:8443", "version": "v1.20.5", "accessible": False}
            ]
        },
        statistics={
            "total_targets": 10,
            "clusters_found": 2,
            "scan_duration": 45.2
        }
    )
    
    # Stockage des résultats
    organizer.store_operation_results(demo_results)
    print("   ✅ Demo results stored")
    
    # Export des résultats
    export_options = ExportOptions(
        format_type="json",
        mask_credentials=True,
        split_by_service=False
    )
    
    exported_files = organizer.export_results(export_options)
    print(f"   ✅ Results exported: {len(exported_files)} files")
    for name, path in exported_files.items():
        print(f"     • {name}: {Path(path).name}")
    
    # Génération du résumé
    summary = organizer.generate_session_summary("demo_session")
    print(f"   ✅ Session summary generated")
    print(f"     • Operations: {summary['total_operations']}")
    print(f"     • Targets: {summary['total_targets']}")
    
    return True


async def demo_k8s_scanner():
    """Démonstration du scanner Kubernetes"""
    print("\n7. 🔍 Kubernetes Scanner Demo")
    
    config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
    
    # Mock logger
    class MockLogger:
        def info(self, msg, **kwargs):
            print(f"   INFO: {msg}")
        def error(self, msg, **kwargs):
            print(f"   ERROR: {msg}")
        def debug(self, msg, **kwargs):
            if config_manager.get_config().core.debug_mode:
                print(f"   DEBUG: {msg}")
    
    scanner = KubernetesScanner(config_manager, MockLogger())
    
    # Test de scan sur localhost (pour démonstration)
    demo_targets = ["127.0.0.1", "localhost"]
    
    print(f"   Scanning {len(demo_targets)} targets...")
    
    all_clusters = []
    for target in demo_targets:
        clusters = await scanner.scan_target(target)
        all_clusters.extend(clusters)
    
    # Statistiques
    stats = scanner.get_statistics()
    print(f"   ✅ Scan completed:")
    print(f"     • Total clusters: {stats['total_clusters']}")
    print(f"     • Accessible: {stats['accessible_clusters']}")
    print(f"     • Vulnerable: {stats['vulnerable_clusters']}")
    
    return True


async def demo_integration():
    """Démonstration d'intégration complète"""
    print("\n8. 🔗 Full Integration Demo")
    
    # Initialisation complète du framework
    engine = WWYVQEngine("wwyvq_v2/configs/default.yaml")
    
    if not await engine.initialize():
        print("   ❌ Failed to initialize engine")
        return False
    
    print("   ✅ Full framework initialized")
    
    # Création d'une session réelle
    session_id = await engine.session_manager.create_session({
        "integration_demo": True,
        "modules_tested": ["core", "validator", "notifier", "exporter", "scanner"]
    })
    
    # Exécution d'une opération de scan
    result = await engine.execute_operation(
        operation_type='scan',
        targets=['127.0.0.1', 'localhost'],
        mode=ExecutionMode.STANDARD
    )
    
    print(f"   ✅ Integration scan completed: {result.operation_id}")
    print(f"   📊 Operation status: {result.status.value}")
    
    # Statistiques finales
    engine_stats = engine.get_engine_stats()
    print(f"   📈 Final engine statistics:")
    print(f"     • Engine ID: {engine_stats['engine_id']}")
    print(f"     • Operations: {engine_stats['operations_completed']}")
    print(f"     • Modules: {engine_stats['modules_loaded']}")
    print(f"     • Status: {engine_stats['status']}")
    
    await engine.shutdown()
    return True


async def main():
    """Démonstration principale"""
    print("🎉 Starting WWYVQ Framework v2 Comprehensive Demo\n")
    
    try:
        # Tests séquentiels
        tests = [
            ("Core Functionality", demo_core_functionality),
            ("Credential Validator", demo_credential_validator),
            ("Telegram Notifier", demo_telegram_notifier),
            ("Results Organizer", demo_results_organizer),
            ("Kubernetes Scanner", demo_k8s_scanner),
            ("Full Integration", demo_integration)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} Demo...")
            try:
                result = await test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                results.append((test_name, False))
        
        # Résumé final
        print("\n" + "=" * 60)
        print("🎉 WWYVQ Framework v2 Demo Results:")
        print("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {status} - {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / len(results)) * 100
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed}/{len(results)})")
        
        if success_rate == 100:
            print("\n🎉 ALL DEMOS PASSED! WWYVQ Framework v2 is ready for production!")
        else:
            print(f"\n⚠️ Some demos failed. Please check the implementation.")
        
        return success_rate == 100
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)