#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Basic Architecture Test
Author: wKayaa
Date: 2025-01-15

Test basique pour valider la nouvelle architecture.
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajout du chemin vers le framework
sys.path.insert(0, str(Path(__file__).parent))

from wwyvq_v2.core import WWYVQEngine, ConfigurationManager, SessionManager, TargetManager, WWYVQLogger
from wwyvq_v2.core.engine import ExecutionMode


async def test_core_components():
    """Test des composants core"""
    print("🧪 Testing WWYVQ Framework v2 Core Components")
    
    # Test 1: Configuration Manager
    print("\n1. Testing Configuration Manager...")
    config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
    config = config_manager.get_config()
    
    print(f"   ✅ Configuration loaded: version {config.version}")
    print(f"   ✅ Max concurrent: {config.core.max_concurrent}")
    print(f"   ✅ Safe mode: {config.core.safe_mode}")
    
    # Test 2: Session Manager
    print("\n2. Testing Session Manager...")
    session_manager = SessionManager(config_manager)
    await session_manager.initialize()
    
    session_id = await session_manager.create_session({"test": "session"})
    print(f"   ✅ Session created: {session_id}")
    
    # Test 3: Target Manager
    print("\n3. Testing Target Manager...")
    target_manager = TargetManager(config_manager)
    await target_manager.initialize()
    
    targets = await target_manager.process_targets(["127.0.0.1", "192.168.1.1"])
    print(f"   ✅ Targets processed: {len(targets)} targets")
    
    # Test 4: Logger
    print("\n4. Testing Logger...")
    logger = WWYVQLogger(config_manager)
    logger.info("Test log message", module="test")
    
    recent_logs = logger.get_recent_logs(limit=5)
    print(f"   ✅ Logger working: {len(recent_logs)} entries")
    
    # Test 5: Engine
    print("\n5. Testing WWYVQ Engine...")
    engine = WWYVQEngine("wwyvq_v2/configs/default.yaml")
    
    init_result = await engine.initialize()
    print(f"   ✅ Engine initialized: {init_result}")
    
    # Test d'opération basique
    print("\n6. Testing Basic Operation...")
    result = await engine.execute_operation(
        operation_type='scan',
        targets=['127.0.0.1'],
        mode=ExecutionMode.STANDARD
    )
    
    print(f"   ✅ Operation completed: {result.operation_id}")
    print(f"   ✅ Status: {result.status.value}")
    
    # Statistiques
    stats = engine.get_engine_stats()
    print(f"\n📊 Engine Statistics:")
    print(f"   Engine ID: {stats['engine_id']}")
    print(f"   Status: {stats['status']}")
    print(f"   Operations: {stats['operations_total']}")
    print(f"   Modules: {stats['modules_loaded']}")
    
    # Nettoyage
    await engine.shutdown()
    print("\n✅ All tests passed!")


async def test_module_loading():
    """Test du chargement des modules"""
    print("\n🧪 Testing Module Loading...")
    
    try:
        from wwyvq_v2.modules.exploit.k8s_scanner import KubernetesScanner
        
        # Test du scanner
        config_manager = ConfigurationManager("wwyvq_v2/configs/default.yaml")
        logger = WWYVQLogger(config_manager)
        
        scanner = KubernetesScanner(config_manager, logger)
        print("   ✅ KubernetesScanner loaded successfully")
        
        # Test des statistiques
        stats = scanner.get_statistics()
        print(f"   ✅ Scanner statistics: {stats}")
        
    except Exception as e:
        print(f"   ❌ Module loading failed: {e}")
        return False
    
    return True


async def test_cli_interface():
    """Test de l'interface CLI"""
    print("\n🧪 Testing CLI Interface...")
    
    try:
        from wwyvq_v2.interfaces.cli import WWYVQCLIInterface
        
        # Mock engine pour le test
        class MockEngine:
            def get_engine_stats(self):
                return {
                    'engine_id': 'test-123',
                    'status': 'running',
                    'uptime_seconds': 60.0,
                    'active_operations': 0,
                    'modules_loaded': 3,
                    'operations_completed': 1,
                    'operations_failed': 0
                }
        
        cli = WWYVQCLIInterface(MockEngine())
        cli.disable_colors()  # Pour les tests
        
        print("   ✅ CLI Interface loaded successfully")
        
        # Test d'affichage
        cli.print_info("Test info message")
        cli.print_success("Test success message")
        cli.print_warning("Test warning message")
        
        print("   ✅ CLI output methods working")
        
    except Exception as e:
        print(f"   ❌ CLI interface test failed: {e}")
        return False
    
    return True


async def main():
    """Test principal"""
    print("🚀 WWYVQ Framework v2 - Architecture Validation Test")
    print("=" * 60)
    
    try:
        # Test des composants core
        await test_core_components()
        
        # Test du chargement des modules
        module_test = await test_module_loading()
        
        # Test de l'interface CLI
        cli_test = await test_cli_interface()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("🎉 WWYVQ Framework v2 Architecture Test Complete!")
        print(f"   Core Components: ✅ PASSED")
        print(f"   Module Loading: {'✅ PASSED' if module_test else '❌ FAILED'}")
        print(f"   CLI Interface: {'✅ PASSED' if cli_test else '❌ FAILED'}")
        
        overall_success = module_test and cli_test
        print(f"\n   Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Exécution du test
    success = asyncio.run(main())
    sys.exit(0 if success else 1)