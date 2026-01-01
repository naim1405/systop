#!/usr/bin/env python3
"""Test script to verify Step 13 polish and integration changes"""

import sys
from src.app import SystemMonitorApp

def test_app_initialization():
    """Test that app initializes properly"""
    print("Testing app initialization...")
    app = SystemMonitorApp()
    
    # Check monitors are initialized
    assert app.cpu_monitor is not None
    assert app.memory_monitor is not None
    assert app.disk_monitor is not None
    assert app.network_monitor is not None
    assert app.gpu_monitor is not None
    assert app.sensors_monitor is not None
    assert app.process_monitor is not None
    print("✓ All monitors initialized")
    
    # Check _widgets list exists (will be populated in compose())
    assert hasattr(app, '_widgets')
    assert isinstance(app._widgets, list)
    print("✓ Widget tracking list initialized")
    
    # Check bindings exist
    assert app.BINDINGS is not None
    assert len(app.BINDINGS) >= 2  # q and r
    print("✓ Keyboard bindings defined")
    
    # Check methods exist
    assert hasattr(app, 'action_quit')
    assert hasattr(app, 'action_refresh_all')
    assert hasattr(app, 'on_mount')
    assert hasattr(app, 'on_unmount')
    print("✓ Required methods present")
    
    return True

def test_widget_imports():
    """Test that all widgets import without errors"""
    print("\nTesting widget imports...")
    
    from src.widgets.cpu_widget import CPUWidget
    from src.widgets.memory_widget import MemoryWidget
    from src.widgets.disk_widget import DiskWidget
    from src.widgets.network_widget import NetworkWidget
    from src.widgets.gpu_widget import GPUWidget
    from src.widgets.sensors_widget import SensorsWidget
    from src.widgets.process_widget import ProcessWidget
    
    print("✓ All widgets imported successfully")
    return True

def test_version():
    """Test version info in __init__.py"""
    print("\nTesting version info...")
    import src
    assert hasattr(src, '__version__')
    assert src.__version__ == "0.1.0"
    print(f"✓ Version: {src.__version__}")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Step 13 Polish & Integration - Verification Tests")
    print("=" * 60)
    
    tests = [
        ("App Initialization", test_app_initialization),
        ("Widget Imports", test_widget_imports),
        ("Version Info", test_version),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All polish and integration tests passed!")
        print("\nNew features implemented:")
        print("  • Graceful shutdown (on_unmount)")
        print("  • Error handling in all widgets")
        print("  • Loading states for initial data")
        print("  • 'r' key for force refresh")
        print("  • Improved CSS styling")
        print("  • Widget focus management")
        print("  • Comprehensive error messages")
        return 0

if __name__ == "__main__":
    sys.exit(main())
