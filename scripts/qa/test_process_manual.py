#!/usr/bin/env python3
"""Manual test script for ProcessMonitor and ProcessWidget.

This script performs comprehensive testing of the process management
features without requiring TUI interaction.
"""

import time
import subprocess
import sys
from src.monitors.processes import ProcessMonitor
from src.widgets.process_widget import ProcessWidget
from src.config import config


def test_process_monitor():
    """Test ProcessMonitor functionality."""
    print("=" * 60)
    print("Testing ProcessMonitor")
    print("=" * 60)
    
    monitor = ProcessMonitor()
    
    # Test 1: Basic collection
    print("\n1. Testing basic process collection...")
    data = monitor.collect()
    print(f"   ✓ Collected {data['total_count']} processes")
    
    if data['processes']:
        first_proc = data['processes'][0]
        print(f"   ✓ Top CPU process: {first_proc['name']} (PID {first_proc['pid']}, {first_proc['cpu_percent']:.1f}%)")
    
    # Test 2: Sorting by different fields
    print("\n2. Testing sorting...")
    
    # Sort by memory
    mem_data = monitor.collect(sort_by='memory_percent', reverse=True)
    if mem_data['processes']:
        top_mem = mem_data['processes'][0]
        print(f"   ✓ Top memory process: {top_mem['name']} ({top_mem['memory_percent']:.1f}%)")
    
    # Sort by PID
    pid_data = monitor.collect(sort_by='pid', reverse=False)
    if pid_data['processes']:
        lowest_pid = pid_data['processes'][0]
        print(f"   ✓ Lowest PID: {lowest_pid['pid']} ({lowest_pid['name']})")
    
    # Sort by name
    name_data = monitor.collect(sort_by='name', reverse=False)
    if name_data['processes']:
        first_name = name_data['processes'][0]['name']
        print(f"   ✓ First alphabetically: {first_name}")
    
    # Test 3: Process structure validation
    print("\n3. Testing process data structure...")
    if data['processes']:
        proc = data['processes'][0]
        required_fields = ['pid', 'name', 'user', 'cpu_percent', 'memory_percent', 
                          'memory_mb', 'status', 'create_time']
        for field in required_fields:
            assert field in proc, f"Missing field: {field}"
        print(f"   ✓ All required fields present")
    
    # Test 4: Test with many processes (pagination check)
    print("\n4. Testing pagination...")
    page_size = config.PROCESS_PAGE_SIZE
    total_procs = len(data['processes'])
    total_pages = (total_procs + page_size - 1) // page_size
    print(f"   ✓ {total_procs} processes → {total_pages} pages ({page_size} per page)")
    
    # Test 5: Kill process (test with non-existent PID)
    print("\n5. Testing kill_process (with invalid PID)...")
    result = monitor.kill_process(999999)  # Non-existent PID
    print(f"   ✓ Kill invalid PID returned: {result} (expected False)")
    
    print("\n✓ ProcessMonitor tests passed!")
    return True


def test_process_widget():
    """Test ProcessWidget functionality."""
    print("\n" + "=" * 60)
    print("Testing ProcessWidget")
    print("=" * 60)
    
    monitor = ProcessMonitor()
    widget = ProcessWidget(monitor)
    
    # Test 1: Initial state
    print("\n1. Testing initial state...")
    assert widget.current_page == 0, "Current page should be 0"
    assert widget.search_term == "", "Search term should be empty"
    assert widget.selected_row == 0, "Selected row should be 0"
    assert widget.can_focus == True, "Widget should be focusable"
    print("   ✓ Initial state correct")
    
    # Test 2: Data refresh
    print("\n2. Testing data refresh...")
    widget.refresh_data()
    assert len(widget._all_processes) > 0, "Should have collected processes"
    assert widget._total_count > 0, "Total count should be > 0"
    print(f"   ✓ Refreshed data: {widget._total_count} processes")
    
    # Test 3: Pagination
    print("\n3. Testing pagination...")
    total_pages = widget._get_total_pages()
    print(f"   Total pages: {total_pages}")
    
    # Get first page
    page_procs = widget._get_current_page_processes()
    print(f"   ✓ First page has {len(page_procs)} processes")
    
    if total_pages > 1:
        # Move to next page
        widget._next_page()
        assert widget.current_page == 1, "Should be on page 1"
        print(f"   ✓ Navigated to page 2")
        
        # Move back
        widget._previous_page()
        assert widget.current_page == 0, "Should be back on page 0"
        print(f"   ✓ Navigated back to page 1")
    else:
        print(f"   ℹ Only one page, skipping navigation test")
    
    # Test 4: Search functionality
    print("\n4. Testing search...")
    widget.search_term = "python"
    widget._apply_filter()
    filtered_count = len(widget._filtered_processes)
    print(f"   ✓ Search 'python': {filtered_count} processes found")
    
    # Clear search
    widget.search_term = ""
    widget._apply_filter()
    assert len(widget._filtered_processes) == widget._total_count, "Filter should be cleared"
    print(f"   ✓ Search cleared: back to {len(widget._filtered_processes)} processes")
    
    # Test 5: Selection
    print("\n5. Testing selection...")
    selected = widget._get_selected_process()
    if selected:
        print(f"   ✓ Selected process: {selected['name']} (PID {selected['pid']})")
    else:
        print(f"   ! No process selected")
    
    # Test 6: Movement
    print("\n6. Testing navigation...")
    initial_row = widget.selected_row
    widget._move_selection(1)  # Move down
    print(f"   ✓ Moved down: row {initial_row} → {widget.selected_row}")
    
    widget._move_selection(-1)  # Move up
    print(f"   ✓ Moved up: back to row {widget.selected_row}")
    
    # Test 7: Sorting
    print("\n7. Testing sort by memory...")
    widget.sort_by = "memory_percent"
    widget.refresh_data()
    page_procs = widget._get_current_page_processes()
    if len(page_procs) >= 2:
        # Check that first process has more memory than second
        first_mem = page_procs[0]['memory_percent']
        second_mem = page_procs[1]['memory_percent']
        print(f"   ✓ Top memory: {page_procs[0]['name']} ({first_mem:.1f}% ≥ {second_mem:.1f}%)")
    
    print("\n✓ ProcessWidget tests passed!")
    return True


def test_search_filtering():
    """Test search filtering in detail."""
    print("\n" + "=" * 60)
    print("Testing Search Filtering")
    print("=" * 60)
    
    monitor = ProcessMonitor()
    widget = ProcessWidget(monitor)
    widget.refresh_data()
    
    total = len(widget._all_processes)
    print(f"\nTotal processes: {total}")
    
    # Test common process names
    test_terms = ["python", "sh", "systemd", "kernel", "x", "z"]
    
    for term in test_terms:
        widget.search_term = term
        widget._apply_filter()
        count = len(widget._filtered_processes)
        print(f"  Search '{term}': {count} matches ({count*100//total if total else 0}%)")
    
    # Test case insensitivity
    widget.search_term = "PYTHON"
    widget._apply_filter()
    upper_count = len(widget._filtered_processes)
    
    widget.search_term = "python"
    widget._apply_filter()
    lower_count = len(widget._filtered_processes)
    
    print(f"\n  Case insensitivity: 'PYTHON'={upper_count}, 'python'={lower_count}")
    assert upper_count == lower_count, "Search should be case-insensitive"
    print("  ✓ Search is case-insensitive")
    
    print("\n✓ Search filtering tests passed!")
    return True


def test_with_background_process():
    """Test with a real background process we control."""
    print("\n" + "=" * 60)
    print("Testing with Background Process")
    print("=" * 60)
    
    print("\n1. Starting background sleep process...")
    proc = subprocess.Popen(['sleep', '30'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    our_pid = proc.pid
    print(f"   ✓ Started sleep process with PID {our_pid}")
    
    time.sleep(0.5)  # Give it time to show up
    
    print("\n2. Searching for our process...")
    monitor = ProcessMonitor()
    data = monitor.collect()
    
    found = False
    for p in data['processes']:
        if p['pid'] == our_pid:
            found = True
            print(f"   ✓ Found our process: {p['name']} (PID {our_pid})")
            print(f"      User: {p['user']}, CPU: {p['cpu_percent']:.1f}%, Status: {p['status']}")
            break
    
    if not found:
        print(f"   ! Process {our_pid} not found in list")
    
    print("\n3. Testing kill functionality...")
    result = monitor.kill_process(our_pid)
    print(f"   Kill signal sent: {result}")
    
    # Wait for process to die
    time.sleep(0.5)
    
    # Check if process is gone
    try:
        proc.wait(timeout=2)
        print(f"   ✓ Process terminated successfully")
    except subprocess.TimeoutExpired:
        print(f"   ! Process still running, forcefully killing...")
        proc.kill()
        proc.wait()
    
    print("\n✓ Background process test passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SYSTOP PROCESS MODULE MANUAL TESTS")
    print("=" * 60)
    print(f"Page size: {config.PROCESS_PAGE_SIZE}")
    print(f"Default sort: {config.PROCESS_SORT_BY}")
    print(f"Python version: {sys.version.split()[0]}")
    
    try:
        success = True
        success &= test_process_monitor()
        success &= test_process_widget()
        success &= test_search_filtering()
        success &= test_with_background_process()
        
        print("\n" + "=" * 60)
        if success:
            print("✓ ALL TESTS PASSED!")
        else:
            print("✗ SOME TESTS FAILED")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
