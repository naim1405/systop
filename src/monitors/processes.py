"""Process monitor for collecting system process information.

This module provides the ProcessMonitor class that collects detailed information
about all running processes on the system, with support for sorting, filtering,
and process termination.
"""

import psutil
from typing import Dict, List, Any
from src.monitors.base import BaseMonitor


class ProcessMonitor(BaseMonitor):
    """Monitor for process information and management.
    
    Collects detailed information about all running processes including PID,
    name, user, CPU usage, memory usage, status, and creation time. Supports
    sorting by any field and killing processes by PID.
    
    Unlike other monitors, ProcessMonitor doesn't maintain history since process
    lists are large and change frequently.
    
    Attributes:
        history: CircularBuffer with size 1 (no historical data needed)
        
    Example:
        monitor = ProcessMonitor()
        data = monitor.collect(sort_by='cpu_percent', reverse=True)
        processes = data['processes']
        
        # Kill a process
        success = monitor.kill_process(12345)
    """
    
    def __init__(self):
        """Initialize the process monitor without history tracking."""
        super().__init__(history_size=1)  # No need for history
        
    def collect(self, sort_by: str = 'cpu_percent', 
                reverse: bool = True) -> Dict[str, Any]:
        """Collect information about all running processes.
        
        Iterates through all system processes and collects detailed information.
        Handles processes that terminate during iteration or that the current
        user doesn't have permission to access.
        
        Args:
            sort_by: Field name to sort by. Valid options:
                    'cpu_percent', 'memory_percent', 'memory_mb', 'pid', 
                    'name', 'user', 'status', 'create_time'
            reverse: If True, sort in descending order (highest first).
                    If False, sort in ascending order (lowest first).
        
        Returns:
            Dictionary containing:
                - processes: List of process dictionaries with fields:
                    - pid: Process ID (int)
                    - name: Process name (str)
                    - user: Username of process owner (str)
                    - cpu_percent: CPU usage percentage (float)
                    - memory_percent: Memory usage percentage (float)
                    - memory_mb: Memory usage in MB (float)
                    - status: Process status (str, e.g., 'running', 'sleeping')
                    - create_time: Process creation timestamp (float)
                - total_count: Total number of processes (int)
        
        Example:
            data = monitor.collect(sort_by='memory_percent', reverse=True)
            top_memory_process = data['processes'][0]
            print(f"Top memory user: {top_memory_process['name']}")
        """
        processes = []
        
        # Iterate through all processes with required attributes
        for proc in psutil.process_iter(['pid', 'name', 'username', 
                                         'cpu_percent', 'memory_percent', 
                                         'memory_info', 'status', 'create_time']):
            try:
                pinfo = proc.info
                
                # Build process dictionary with all required fields
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'] or 'N/A',
                    'user': pinfo['username'] or 'N/A',
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'memory_mb': pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0.0,
                    'status': pinfo['status'] or 'unknown',
                    'create_time': pinfo['create_time'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process terminated during iteration or we don't have permission
                # Skip and continue with next process
                pass
            except Exception:
                # Catch any other unexpected errors and continue
                pass
        
        # Sort processes by the specified field
        try:
            processes.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        except (KeyError, TypeError):
            # Invalid sort field or comparison error, use default sorting
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        # Store minimal data in history (just count for BaseMonitor compatibility)
        self._last_data = {
            'processes': processes,
            'total_count': len(processes)
        }
        
        return self._last_data
    
    def kill_process(self, pid: int) -> bool:
        """Attempt to terminate a process by PID.
        
        Sends a SIGTERM signal to the specified process. This is a graceful
        shutdown request that allows the process to clean up before exiting.
        
        Args:
            pid: Process ID to terminate
        
        Returns:
            True if the termination signal was successfully sent.
            False if the process doesn't exist or permission was denied.
        
        Note:
            - This method sends SIGTERM, not SIGKILL. The process may take
              time to shut down or may ignore the signal.
            - Requires appropriate permissions. Regular users can only kill
              their own processes.
            - Root/sudo access is required to kill processes owned by others.
        
        Example:
            if monitor.kill_process(12345):
                print("Process termination signal sent")
            else:
                print("Failed to kill process (not found or permission denied)")
        """
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except psutil.NoSuchProcess:
            # Process doesn't exist (may have already terminated)
            return False
        except psutil.AccessDenied:
            # Don't have permission to kill this process
            return False
        except Exception:
            # Any other error (connection lost, etc.)
            return False
