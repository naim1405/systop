#!/usr/bin/env python3
"""
Quick 5-minute stability test for systop
Monitors memory and CPU usage
"""

import subprocess
import time
import psutil
import signal
import sys

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\nTest interrupted by user')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('='*70)
print('systop - Quick Stability Test (5 minutes)')
print('='*70)
print()
print('This test will:')
print('  1. Start systop in background')
print('  2. Monitor memory and CPU usage every 30 seconds')
print('  3. Report any memory growth or high CPU usage')
print()
print('Starting test...')
print('-'*70)

# Start systop
proc = subprocess.Popen(
    ['python', 'main.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(3)  # Let it start

try:
    # Verify it's running
    if proc.poll() is not None:
        print('ERROR: systop exited immediately!')
        sys.exit(1)
    
    # Get process object
    systop_proc = psutil.Process(proc.pid)
    
    print(f'systop started (PID: {proc.pid})')
    print(f'Start time: {time.strftime("%H:%M:%S")}')
    print()
    print(f'{"Time":<12} {"RSS (MB)":<12} {"VMS (MB)":<12} {"CPU %":<8}')
    print('-'*50)
    
    measurements = []
    
    # Monitor for 5 minutes (10 samples, 30 seconds apart)
    for i in range(10):
        # Check if still running
        if proc.poll() is not None:
            print('\nERROR: systop crashed during test!')
            sys.exit(1)
        
        # Get metrics
        mem_info = systop_proc.memory_info()
        cpu_percent = systop_proc.cpu_percent(interval=1.0)
        
        rss_mb = mem_info.rss / 1024 / 1024
        vms_mb = mem_info.vms / 1024 / 1024
        
        measurements.append({
            'time': time.time(),
            'rss': rss_mb,
            'vms': vms_mb,
            'cpu': cpu_percent
        })
        
        timestamp = time.strftime('%H:%M:%S')
        print(f'{timestamp:<12} {rss_mb:<12.1f} {vms_mb:<12.1f} {cpu_percent:<8.1f}')
        
        # Sleep (except on last iteration)
        if i < 9:
            time.sleep(30)
    
    print()
    print('='*70)
    print('TEST RESULTS')
    print('='*70)
    
    # Calculate statistics
    initial_rss = measurements[0]['rss']
    final_rss = measurements[-1]['rss']
    max_rss = max(m['rss'] for m in measurements)
    min_rss = min(m['rss'] for m in measurements)
    avg_rss = sum(m['rss'] for m in measurements) / len(measurements)
    avg_cpu = sum(m['cpu'] for m in measurements) / len(measurements)
    
    growth = final_rss - initial_rss
    growth_pct = (growth / initial_rss) * 100 if initial_rss > 0 else 0
    
    print()
    print('Memory Statistics:')
    print(f'  Initial RSS:  {initial_rss:8.1f} MB')
    print(f'  Final RSS:    {final_rss:8.1f} MB')
    print(f'  Average RSS:  {avg_rss:8.1f} MB')
    print(f'  Range:        {min_rss:.1f} - {max_rss:.1f} MB')
    print(f'  Growth:       {growth:+8.1f} MB ({growth_pct:+.1f}%)')
    print()
    print('CPU Statistics:')
    print(f'  Average CPU:  {avg_cpu:8.1f} %')
    print()
    
    # Evaluation
    print('Evaluation:')
    
    memory_ok = abs(growth_pct) < 20
    cpu_ok = avg_cpu < 15
    
    if memory_ok:
        print('  ✅ Memory: PASS (stable usage, no significant growth)')
    else:
        print(f'  ❌ Memory: FAIL (growth of {growth_pct:.1f}% detected)')
    
    if cpu_ok:
        print('  ✅ CPU: PASS (reasonable usage)')
    else:
        print(f'  ⚠️  CPU: WARNING (average {avg_cpu:.1f}% may be high)')
    
    print()
    
    if memory_ok and cpu_ok:
        print('='*70)
        print('✅ OVERALL: PASS')
        print('='*70)
        print()
        print('systop is stable and ready for extended testing.')
        print('Run the full 30-minute test with: python test_final_verification.py')
    else:
        print('='*70)
        print('⚠️  OVERALL: NEEDS REVIEW')
        print('='*70)
        print()
        print('Some metrics exceeded thresholds.')
        print('Please investigate further.')
    
except Exception as e:
    print(f'\nERROR during test: {e}')
    import traceback
    traceback.print_exc()
finally:
    # Cleanup
    print()
    print('Stopping systop...')
    proc.terminate()
    try:
        proc.wait(timeout=5)
        print('systop stopped cleanly.')
    except subprocess.TimeoutExpired:
        print('Forcing systop to stop...')
        proc.kill()
        proc.wait()
    
    print()
    print('Test complete.')
