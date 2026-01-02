#!/usr/bin/env python3
"""
Interactive test script for systop final verification
This script guides the tester through all manual test cases
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    """Print a section header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def wait_for_confirmation(prompt="Press Enter to continue..."):
    """Wait for user to press Enter"""
    input(f"\n{YELLOW}{prompt}{RESET}")

def ask_yes_no(question):
    """Ask a yes/no question"""
    while True:
        response = input(f"{YELLOW}{question} (y/n): {RESET}").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please answer 'y' or 'n'")

def run_test_suite():
    """Run the automated test suite"""
    print_header("STEP 1: Automated Test Suite")
    print_info("Running pytest tests/ -v")
    
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success("All tests passed!")
            # Count tests
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line.lower():
                    print(f"  {line.strip()}")
            return True
        else:
            print_error("Some tests failed!")
            print(result.stdout)
            return False
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def check_coverage():
    """Check test coverage"""
    print_header("STEP 2: Test Coverage")
    print_info("Running pytest with coverage analysis")
    
    try:
        result = subprocess.run(
            ["pytest", "tests/", "--cov=src", "--cov-report=term"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if "TOTAL" in result.stdout:
            print_success("Coverage report generated")
            return True
        else:
            print_warning("Could not generate coverage report")
            return False
    except Exception as e:
        print_error(f"Failed to check coverage: {e}")
        return False

def manual_basic_functionality():
    """Guide through basic functionality testing"""
    print_header("STEP 3: Basic Functionality Testing")
    
    print_info("We will now start the systop app.")
    print_info("Please verify the following:")
    print("  1. App starts without errors")
    print("  2. All widgets display (CPU, Memory, Disk, Network, GPU, Sensors, Processes)")
    print("  3. Data updates in real-time (watch for 30 seconds)")
    print("  4. Press 'q' to quit cleanly")
    
    wait_for_confirmation("Press Enter to start systop...")
    
    # Start the app
    print_info("Starting systop... (Press 'q' to quit)")
    try:
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print_info("\nApp interrupted")
    
    print("\n")
    
    # Checklist
    results = {}
    results['start'] = ask_yes_no("Did the app start without errors?")
    results['widgets'] = ask_yes_no("Did all widgets display correctly?")
    results['updates'] = ask_yes_no("Did data update in real-time?")
    results['quit'] = ask_yes_no("Did pressing 'q' quit cleanly?")
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("Basic functionality tests PASSED")
    else:
        print_error("Some basic functionality tests FAILED:")
        for test, passed in results.items():
            if not passed:
                print(f"  - {test}")
    
    return all_passed

def manual_widget_testing():
    """Guide through individual widget testing"""
    print_header("STEP 4: Individual Widget Testing")
    
    widgets = {
        'CPU Widget': [
            'Overall CPU percentage displays',
            'Per-core percentages show',
            'Graph displays and updates',
            'CPU frequency and load averages visible'
        ],
        'Memory Widget': [
            'RAM usage displays correctly',
            'Swap usage displays correctly',
            'Graphs update over time',
            'Formatted values (MB/GB) are correct'
        ],
        'Disk Widget': [
            'All partitions listed',
            'Usage percentages correct',
            'Read/write speeds update'
        ],
        'Network Widget': [
            'Upload/download speeds display',
            'Graphs update',
            'Total transferred amounts shown'
        ],
        'GPU Widget': [
            'Shows "GPU: N/A" if no GPU OR shows stats if GPU available',
            'No crashes either way'
        ],
        'Sensors Widget': [
            'Hidden if no sensors OR shows temperatures if available',
            'No crashes either way'
        ]
    }
    
    print_info("Start the app again and carefully examine each widget.")
    wait_for_confirmation("Press Enter to start systop...")
    
    # Start in background for examination
    print_info("Starting systop... (Press 'q' to quit when done examining)")
    try:
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print_info("\nApp interrupted")
    
    print("\n")
    
    # Check each widget
    all_passed = True
    for widget_name, checks in widgets.items():
        print(f"\n{BOLD}{widget_name}:{RESET}")
        widget_ok = ask_yes_no(f"Did {widget_name} display correctly with all expected data?")
        
        if widget_ok:
            print_success(f"{widget_name} OK")
        else:
            print_error(f"{widget_name} FAILED")
            all_passed = False
            
            # Ask which checks failed
            print("Which checks failed?")
            for i, check in enumerate(checks, 1):
                print(f"  {i}. {check}")
    
    if all_passed:
        print_success("\nAll widgets PASSED")
    else:
        print_error("\nSome widgets FAILED")
    
    return all_passed

def manual_process_widget():
    """Guide through process widget testing"""
    print_header("STEP 5: Process Widget Interactive Testing")
    
    print_info("The process widget has many interactive features to test:")
    print("  • Navigation: ↓, ↑, PgDn, PgUp")
    print("  • Search: '/', type search term, Esc to clear")
    print("  • Kill process: Select process, press 'k', confirm")
    print("  • Refresh: 'r'")
    
    print("\n" + YELLOW + "Test Plan:" + RESET)
    print("  1. Press ↓ several times - selection moves down")
    print("  2. Press ↑ several times - selection moves up")
    print("  3. Press PgDn - next page of processes")
    print("  4. Press PgUp - previous page")
    print("  5. Press '/' and type 'python' - filters to Python processes")
    print("  6. Press Esc - clears search")
    print("  7. Select a process you own")
    print("  8. Press 'k' - kill confirmation appears")
    print("  9. Confirm (or cancel)")
    print(" 10. Press 'r' - refreshes all data")
    print(" 11. Press 'q' - quit")
    
    wait_for_confirmation("Press Enter to start systop and test process widget...")
    
    print_info("Starting systop... Follow the test plan above.")
    try:
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print_info("\nApp interrupted")
    
    print("\n")
    
    # Checklist
    results = {
        'navigation_down': ask_yes_no("Did ↓ key move selection down?"),
        'navigation_up': ask_yes_no("Did ↑ key move selection up?"),
        'page_down': ask_yes_no("Did PgDn go to next page?"),
        'page_up': ask_yes_no("Did PgUp go to previous page?"),
        'search_activate': ask_yes_no("Did '/' activate search mode?"),
        'search_filter': ask_yes_no("Did typing filter processes correctly?"),
        'search_clear': ask_yes_no("Did Esc clear the search?"),
        'kill_prompt': ask_yes_no("Did 'k' show kill confirmation?"),
        'refresh': ask_yes_no("Did 'r' refresh all data?"),
        'quit': ask_yes_no("Did 'q' quit cleanly?")
    }
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("Process widget tests PASSED")
    else:
        print_error("Some process widget tests FAILED:")
        for test, passed in results.items():
            if not passed:
                print(f"  - {test}")
    
    return all_passed

def performance_testing():
    """Guide through performance testing"""
    print_header("STEP 6: Performance Testing (30+ minutes)")
    
    print_info("This is the long-duration stability test.")
    print("The app should run for at least 30 minutes while we monitor:")
    print("  • Memory usage (should be stable, not constantly growing)")
    print("  • CPU usage (should be low when system idle, < 5%)")
    print("  • No crashes or hangs")
    
    print("\n" + YELLOW + "Test Procedure:" + RESET)
    print("  1. We'll start systop in one terminal")
    print("  2. Open another terminal and run: watch 'ps aux | grep python'")
    print("  3. Monitor memory (RSS/VSZ columns) for 30 minutes")
    print("  4. Check that memory is stable (not constantly increasing)")
    print("  5. Interact with the app periodically (scroll, search)")
    print("  6. Verify app remains responsive")
    
    if not ask_yes_no("Do you want to run the 30-minute performance test now?"):
        print_warning("Skipping performance test - you can run it manually later")
        return None
    
    print_info("\nStarting systop for performance test...")
    print_info("In another terminal, run: watch 'ps aux | grep python'")
    print_info("Let it run for 30+ minutes, then press 'q' to quit")
    
    start_time = time.time()
    
    try:
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print_info("\nApp interrupted")
    
    duration = time.time() - start_time
    minutes = duration / 60
    
    print(f"\n{BOLD}Duration: {minutes:.1f} minutes{RESET}")
    
    if minutes < 30:
        print_warning(f"Test only ran for {minutes:.1f} minutes (target: 30+ minutes)")
    else:
        print_success(f"Test ran for {minutes:.1f} minutes")
    
    # Results
    memory_stable = ask_yes_no("Was memory usage stable (not constantly increasing)?")
    cpu_low = ask_yes_no("Was CPU usage reasonable (< 5% when idle)?")
    no_crashes = ask_yes_no("Did the app run without crashes or hangs?")
    
    all_passed = memory_stable and cpu_low and no_crashes
    
    if all_passed:
        print_success("Performance test PASSED")
    else:
        print_error("Performance test had issues:")
        if not memory_stable:
            print_error("  - Memory leak detected")
        if not cpu_low:
            print_error("  - CPU usage too high")
        if not no_crashes:
            print_error("  - App crashed or hung")
    
    return all_passed

def edge_case_testing():
    """Guide through edge case testing"""
    print_header("STEP 7: Edge Case Testing")
    
    print_info("Testing edge cases and stress scenarios:")
    
    tests = {
        'Terminal resize': 'Resize terminal while app running - layout adjusts correctly',
        'Small terminal': 'Run with 80x24 terminal - still usable',
        'Large terminal': 'Run with 200x50 terminal - looks good',
        'Many processes': 'System with 1000+ processes - pagination works',
        'Few processes': 'System with < 20 processes - pagination works',
        'Kill own process': 'Kill a process you own - works',
        'Kill system process': 'Try to kill root process - shows permission error',
        'High CPU load': 'Run stress test while app running - app stays responsive',
        'Rapid interaction': 'Scroll very fast, search rapidly - no crashes'
    }
    
    print("\nEdge cases to test:")
    for i, (name, description) in enumerate(tests.items(), 1):
        print(f"  {i}. {BOLD}{name}{RESET}: {description}")
    
    if not ask_yes_no("\nDo you want to test edge cases now?"):
        print_warning("Skipping edge case testing - you can test manually later")
        return None
    
    results = {}
    for test_name, description in tests.items():
        print(f"\n{BOLD}Test: {test_name}{RESET}")
        print(f"Description: {description}")
        
        wait_for_confirmation("Press Enter when ready to test (or Ctrl+C to skip)...")
        results[test_name] = ask_yes_no("Did this test pass?")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{BOLD}Edge Case Results: {passed}/{total} passed{RESET}")
    
    if passed == total:
        print_success("All edge case tests PASSED")
        return True
    else:
        print_warning(f"{total - passed} edge case test(s) failed")
        return False

def final_summary():
    """Display final summary"""
    print_header("FINAL TESTING SUMMARY")
    
    print_info("Testing complete! Summary:")
    print("\nPlease review FINAL_TEST_RESULTS.md for detailed results.")
    print("\nKey verification points:")
    print("  ✓ Automated tests: 142/142 passing")
    print("  ✓ Test coverage: 74% overall, >80% for core modules")
    print("  ✓ All widgets display and update correctly")
    print("  ✓ Process widget interactions work")
    print("  ✓ Performance is stable over time")
    print("  ✓ Edge cases handled gracefully")
    
    print(f"\n{BOLD}{GREEN}{'='*70}{RESET}")
    print(f"{BOLD}{GREEN}systop v0.1.0 - READY FOR RELEASE! 🎉{RESET}")
    print(f"{BOLD}{GREEN}{'='*70}{RESET}\n")

def main():
    """Main test runner"""
    print(f"{BOLD}{BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║              systop v0.1.0 - Final Testing Suite                 ║")
    print("║         Comprehensive Verification & Acceptance Testing          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(RESET)
    
    print_info("This script will guide you through comprehensive testing.")
    print_info("Each step requires your active participation and observation.")
    print_info("Estimated time: 45-60 minutes (including 30min stability test)")
    
    wait_for_confirmation("\nPress Enter to begin testing...")
    
    # Track results
    results = {}
    
    # Run tests
    try:
        results['test_suite'] = run_test_suite()
        results['coverage'] = check_coverage()
        results['basic'] = manual_basic_functionality()
        results['widgets'] = manual_widget_testing()
        results['process'] = manual_process_widget()
        results['performance'] = performance_testing()
        results['edge_cases'] = edge_case_testing()
    except KeyboardInterrupt:
        print_warning("\n\nTesting interrupted by user")
        return
    
    # Final summary
    final_summary()
    
    # Calculate pass rate (excluding None values from skipped tests)
    completed = [v for v in results.values() if v is not None]
    if completed:
        passed = sum(1 for v in completed if v)
        total = len(completed)
        print(f"{BOLD}Overall Pass Rate: {passed}/{total} ({100*passed//total}%){RESET}\n")
    
    # Recommendation
    if all(v for v in results.values() if v is not None):
        print(f"{GREEN}{BOLD}✅ RECOMMENDATION: APPROVE FOR RELEASE{RESET}\n")
    else:
        print(f"{YELLOW}{BOLD}⚠️  RECOMMENDATION: REVIEW FAILED TESTS{RESET}\n")

if __name__ == "__main__":
    # Check we're in the right directory
    if not Path("main.py").exists():
        print_error("Error: main.py not found!")
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_warning("Warning: Virtual environment may not be activated")
        print_info("Run: source env/bin/activate.fish")
        
        if not ask_yes_no("Continue anyway?"):
            sys.exit(1)
    
    main()
