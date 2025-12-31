"""CPU monitoring module for collecting CPU metrics.

This module provides the CPUMonitor class that collects comprehensive CPU
metrics including overall and per-core usage, frequency, load averages, and
CPU information using psutil and py-cpuinfo.
"""

import os
from typing import Dict, Any, List
import psutil
import cpuinfo
from src.monitors.base import BaseMonitor


class CPUMonitor(BaseMonitor):
    """Monitor for CPU metrics.
    
    Collects and tracks CPU usage, frequency, load averages, and hardware info.
    Maintains historical data for overall CPU percentage for graphing.
    
    Attributes:
        _cpu_info: Dictionary containing CPU hardware information from cpuinfo
        
    Example:
        monitor = CPUMonitor(history_size=60)
        data = monitor.collect()
        print(f"CPU Usage: {data['overall_percent']}%")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize CPU monitor with CPU hardware information.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-second data.
        """
        super().__init__(history_size)
        self._cpu_info = cpuinfo.get_cpu_info()
    
    def collect(self) -> Dict[str, Any]:
        """Collect current CPU metrics.
        
        Gathers comprehensive CPU information including usage percentages,
        frequency, load averages, core counts, and model information.
        The overall CPU percentage is stored in history for time-series graphs.
        
        Returns:
            Dictionary containing:
                - overall_percent: Overall CPU usage percentage (float)
                - per_core_percent: List of per-core usage percentages (List[float])
                - frequency: Current, min, and max frequencies in MHz (Dict)
                - load_avg: System load averages for 1, 5, 15 minutes (Dict)
                - cpu_count: Physical and logical core counts (Dict)
                - model: CPU model name string (str)
                
        Example:
            {
                'overall_percent': 45.2,
                'per_core_percent': [50.0, 40.5, 48.3, 42.1],
                'frequency': {'current': 2400.0, 'min': 800.0, 'max': 3500.0},
                'load_avg': {'1min': 1.5, '5min': 1.2, '15min': 0.9},
                'cpu_count': {'physical': 2, 'logical': 4},
                'model': 'Intel Core i5-8250U'
            }
        """
        # Get overall CPU percentage
        overall_percent = psutil.cpu_percent(interval=None)
        
        # Get per-core CPU percentages
        per_core_percent = psutil.cpu_percent(interval=None, percpu=True)
        
        # Get CPU frequency information
        freq = psutil.cpu_freq()
        frequency = {
            'current': freq.current if freq else 0.0,
            'min': freq.min if freq else 0.0,
            'max': freq.max if freq else 0.0
        }
        
        # Get load averages (1min, 5min, 15min)
        load_1, load_5, load_15 = os.getloadavg()
        load_avg = {
            '1min': load_1,
            '5min': load_5,
            '15min': load_15
        }
        
        # Get CPU counts
        cpu_count = {
            'physical': psutil.cpu_count(logical=False) or 0,
            'logical': psutil.cpu_count(logical=True) or 0
        }
        
        # Get CPU model name
        model = self._cpu_info.get('brand_raw', 'Unknown CPU')
        
        # Build data dictionary
        data = {
            'overall_percent': overall_percent,
            'per_core_percent': per_core_percent,
            'frequency': frequency,
            'load_avg': load_avg,
            'cpu_count': cpu_count,
            'model': model
        }
        
        # Store overall percentage in history for graphing
        self.history.append(overall_percent)
        
        # Store as last data
        self._last_data = data
        
        return data
