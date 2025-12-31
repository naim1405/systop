"""Memory monitoring module for collecting RAM and swap metrics.

This module provides the MemoryMonitor class that collects comprehensive memory
metrics including RAM and swap usage information using psutil.
"""

from typing import Dict, Any
import psutil
from src.monitors.base import BaseMonitor


class MemoryMonitor(BaseMonitor):
    """Monitor for memory and swap metrics.
    
    Collects and tracks RAM and swap usage information.
    Maintains historical data for RAM percentage for graphing.
    
    Example:
        monitor = MemoryMonitor(history_size=60)
        data = monitor.collect()
        print(f"RAM Usage: {data['ram']['percent']}%")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize memory monitor.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-second data.
        """
        super().__init__(history_size)
    
    def collect(self) -> Dict[str, Any]:
        """Collect current memory metrics.
        
        Gathers comprehensive memory information including RAM and swap usage.
        The RAM percentage is stored in history for time-series graphs.
        
        Returns:
            Dictionary containing:
                - ram: Dictionary with total, available, used, free, percent (Dict)
                - swap: Dictionary with total, used, free, percent (Dict)
                
        Example:
            {
                'ram': {
                    'total': 16777216000,
                    'available': 8388608000,
                    'used': 8388608000,
                    'free': 2097152000,
                    'percent': 50.0
                },
                'swap': {
                    'total': 4194304000,
                    'used': 1048576000,
                    'free': 3145728000,
                    'percent': 25.0
                }
            }
        """
        # Get RAM information
        vm = psutil.virtual_memory()
        ram = {
            'total': vm.total,
            'available': vm.available,
            'used': vm.used,
            'free': vm.free,
            'percent': vm.percent
        }
        
        # Get swap information
        swap = psutil.swap_memory()
        swap_data = {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        }
        
        # Build data dictionary
        data = {
            'ram': ram,
            'swap': swap_data
        }
        
        # Store RAM percentage in history for graphing
        self.history.append(ram['percent'])
        
        # Store as last data
        self._last_data = data
        
        return data
