"""Network monitoring module for collecting bandwidth and traffic metrics.

This module provides the NetworkMonitor class that collects comprehensive
network metrics including bandwidth rates and cumulative statistics using psutil.
"""

import time
from typing import Dict, Any, Optional
import psutil
from src.monitors.base import BaseMonitor


class NetworkMonitor(BaseMonitor):
    """Monitor for network bandwidth and traffic metrics.
    
    Collects and tracks network interface statistics including bandwidth rates
    (upload/download speeds) and cumulative byte/packet counts. Maintains
    historical data for bandwidth rates for graphing.
    
    Attributes:
        _last_stats: Dictionary storing previous network counters and timestamp
                    for calculating per-second rates. None on first call.
        
    Example:
        monitor = NetworkMonitor(history_size=60)
        data = monitor.collect()
        print(f"Download: {data['bytes_recv_per_sec']} B/s")
        print(f"Upload: {data['bytes_sent_per_sec']} B/s")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize network monitor.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-second data.
        """
        super().__init__(history_size)
        self._last_stats = None
    
    def collect(self) -> Dict[str, Any]:
        """Collect current network metrics.
        
        Gathers comprehensive network information including bandwidth rates
        and cumulative statistics. Calculates per-second upload/download rates
        by comparing with previous measurements. The total bandwidth rate
        (sent + received) is stored in history for time-series graphs.
        
        On the first call, rates will be 0.0 since there's no previous
        measurement to compare against. Subsequent calls will provide accurate
        per-second rates.
        
        Returns:
            Dictionary containing:
                - bytes_sent_per_sec: Upload speed in bytes per second (float)
                - bytes_recv_per_sec: Download speed in bytes per second (float)
                - total_sent: Cumulative bytes sent since boot (int)
                - total_recv: Cumulative bytes received since boot (int)
                - packets_sent: Cumulative packets sent (int)
                - packets_recv: Cumulative packets received (int)
                
        Example:
            {
                'bytes_sent_per_sec': 524288.0,
                'bytes_recv_per_sec': 1048576.0,
                'total_sent': 1073741824,
                'total_recv': 5368709120,
                'packets_sent': 1000000,
                'packets_recv': 2000000
            }
        """
        # Collect network I/O counters
        current_stats = psutil.net_io_counters()
        current_time = time.time()
        
        # Initialize result with cumulative totals
        result = {
            'bytes_sent_per_sec': 0.0,
            'bytes_recv_per_sec': 0.0,
            'total_sent': 0 if current_stats is None else current_stats.bytes_sent,
            'total_recv': 0 if current_stats is None else current_stats.bytes_recv,
            'packets_sent': 0 if current_stats is None else current_stats.packets_sent,
            'packets_recv': 0 if current_stats is None else current_stats.packets_recv
        }
        
        # Calculate bandwidth rates if we have previous data
        if current_stats is not None and self._last_stats is not None:
            # Calculate time delta
            time_delta = current_time - self._last_stats['timestamp']
            
            if time_delta > 0:
                # Calculate per-second rates
                sent_delta = current_stats.bytes_sent - self._last_stats['bytes_sent']
                recv_delta = current_stats.bytes_recv - self._last_stats['bytes_recv']
                
                result['bytes_sent_per_sec'] = sent_delta / time_delta
                result['bytes_recv_per_sec'] = recv_delta / time_delta
        
        # Store current stats for next calculation
        if current_stats is not None:
            self._last_stats = {
                'bytes_sent': current_stats.bytes_sent,
                'bytes_recv': current_stats.bytes_recv,
                'timestamp': current_time
            }
        
        # Store total bandwidth rate in history (sent + received combined)
        total_bandwidth = result['bytes_sent_per_sec'] + result['bytes_recv_per_sec']
        self.history.append(total_bandwidth)
        
        self._last_data = result
        return result
