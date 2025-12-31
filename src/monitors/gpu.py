"""GPU monitoring module for collecting GPU metrics with graceful fallback.

This module provides the GPUMonitor class that collects GPU metrics including
utilization, memory usage, and temperature using GPUtil. If GPUtil is not
available or no GPU is detected, it gracefully returns None to allow the
application to display "N/A" instead of crashing.
"""

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from typing import Dict, Any, Optional, List
from src.monitors.base import BaseMonitor


class GPUMonitor(BaseMonitor):
    """Monitor for GPU metrics with graceful fallback.
    
    Collects GPU utilization, memory usage, and temperature. If GPUtil is not
    installed or no GPU is detected, returns None to indicate unavailability.
    
    Attributes:
        available: Boolean indicating if GPU monitoring is available
        
    Example:
        monitor = GPUMonitor()
        data = monitor.collect()
        if data is None:
            print("GPU: N/A")
        else:
            print(f"GPU Load: {data[0]['load']}%")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize GPU monitor and check GPU availability.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-2-second data.
        """
        super().__init__(history_size)
        self.available = GPU_AVAILABLE and self._check_gpus()
    
    def _check_gpus(self) -> bool:
        """Check if GPUs are actually available on the system.
        
        Returns:
            True if one or more GPUs are detected, False otherwise.
        """
        if not GPU_AVAILABLE:
            return False
        
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except Exception:
            return False
    
    def collect(self) -> Optional[List[Dict[str, Any]]]:
        """Collect current GPU metrics for all available GPUs.
        
        Returns None if GPU is not available or an error occurs.
        Otherwise returns a list of dictionaries, one per GPU.
        
        Returns:
            None if GPU unavailable, otherwise list of dictionaries containing:
                - id: GPU index (int)
                - name: GPU model name (str)
                - load: GPU utilization percentage 0-100 (float)
                - memory_used: Used memory in MB (float)
                - memory_total: Total memory in MB (float)
                - temperature: GPU temperature in Celsius (float)
                
        Example:
            [
                {
                    'id': 0,
                    'name': 'NVIDIA GeForce RTX 3080',
                    'load': 75.5,
                    'memory_used': 8192.0,
                    'memory_total': 10240.0,
                    'temperature': 65.0
                }
            ]
        """
        if not self.available:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            
            if not gpus:
                return None
            
            gpu_data = []
            for gpu in gpus:
                data = {
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,  # Convert from 0-1 to 0-100
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'temperature': gpu.temperature
                }
                gpu_data.append(data)
                
                # Store the load in history for the first GPU (for graphing)
                if gpu.id == 0:
                    self.history.append(data['load'])
            
            self._last_data = gpu_data
            return gpu_data
            
        except Exception:
            return None
