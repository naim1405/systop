"""Disk monitoring module for collecting disk usage and I/O metrics.

This module provides the DiskMonitor class that collects comprehensive disk
metrics including partition usage and I/O rates using psutil.
"""

import time
from typing import Dict, Any, List, Optional
import psutil
from src.monitors.base import BaseMonitor


class DiskMonitor(BaseMonitor):
    """Monitor for disk usage and I/O metrics.
    
    Collects and tracks disk partition usage and I/O rates (read/write speeds).
    Maintains historical data for I/O rates for graphing.
    
    Attributes:
        _last_io: Dictionary storing previous I/O counters and timestamp for
                 calculating per-second rates. None on first call.
        
    Example:
        monitor = DiskMonitor(history_size=60)
        data = monitor.collect()
        print(f"Read Speed: {data['io']['read_bytes_per_sec']} B/s")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize disk monitor.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-second data.
        """
        super().__init__(history_size)
        self._last_io = None
    
    def collect(self) -> Dict[str, Any]:
        """Collect current disk metrics.
        
        Gathers comprehensive disk information including partition usage and
        I/O rates. Calculates per-second read/write rates by comparing with
        previous measurements. The total I/O rate (read + write) is stored in
        history for time-series graphs.
        
        Returns:
            Dictionary containing:
                - partitions: List of partition dictionaries with device,
                             mountpoint, fstype, total, used, free, percent (List[Dict])
                - io: Dictionary with read_bytes_per_sec, write_bytes_per_sec,
                     read_count, write_count (Dict)
                
        Example:
            {
                'partitions': [
                    {
                        'device': '/dev/sda1',
                        'mountpoint': '/',
                        'fstype': 'ext4',
                        'total': 500000000000,
                        'used': 250000000000,
                        'free': 250000000000,
                        'percent': 50.0
                    }
                ],
                'io': {
                    'read_bytes_per_sec': 1048576.0,
                    'write_bytes_per_sec': 524288.0,
                    'read_count': 1000,
                    'write_count': 500
                }
            }
        """
        # Collect partition information
        partitions = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except (PermissionError, OSError):
                # Skip partitions we can't access (e.g., unmounted drives)
                continue
        
        # Collect I/O counters
        current_io = psutil.disk_io_counters()
        current_time = time.time()
        
        # Calculate I/O rates
        io_data = {
            'read_bytes_per_sec': 0.0,
            'write_bytes_per_sec': 0.0,
            'read_count': 0 if current_io is None else current_io.read_count,
            'write_count': 0 if current_io is None else current_io.write_count
        }
        
        if current_io is not None and self._last_io is not None:
            # Calculate time delta
            time_delta = current_time - self._last_io['timestamp']
            
            if time_delta > 0:
                # Calculate per-second rates
                read_delta = current_io.read_bytes - self._last_io['read_bytes']
                write_delta = current_io.write_bytes - self._last_io['write_bytes']
                
                io_data['read_bytes_per_sec'] = read_delta / time_delta
                io_data['write_bytes_per_sec'] = write_delta / time_delta
        
        # Store current I/O counters for next calculation
        if current_io is not None:
            self._last_io = {
                'read_bytes': current_io.read_bytes,
                'write_bytes': current_io.write_bytes,
                'timestamp': current_time
            }
        
        # Store total I/O rate in history (read + write combined)
        total_io_rate = io_data['read_bytes_per_sec'] + io_data['write_bytes_per_sec']
        self.history.append(total_io_rate)
        
        # Prepare result
        result = {
            'partitions': partitions,
            'io': io_data
        }
        
        self._last_data = result
        return result
