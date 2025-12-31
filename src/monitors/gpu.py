"""GPU monitoring module for collecting GPU metrics with graceful fallback.

This module provides the GPUMonitor class that collects GPU metrics including
utilization, memory usage, and temperature using pynvml (NVIDIA Management Library).
If pynvml is not available or no GPU is detected, it gracefully returns None to 
allow the application to display "N/A" instead of crashing.

Note: Only NVIDIA GPUs are supported via pynvml. AMD GPUs are not currently supported.
"""

try:
    # Try nvidia-ml-py first (official package)
    from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex
    from pynvml import nvmlDeviceGetName, nvmlDeviceGetUtilizationRates
    from pynvml import nvmlDeviceGetMemoryInfo, nvmlDeviceGetTemperature
    from pynvml import nvmlShutdown, NVML_TEMPERATURE_GPU
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from typing import Dict, Any, Optional, List
from src.monitors.base import BaseMonitor


class GPUMonitor(BaseMonitor):
    """Monitor for GPU metrics with graceful fallback.
    
    Collects NVIDIA GPU utilization, memory usage, and temperature using pynvml.
    If pynvml is not installed or no GPU is detected, returns None to indicate 
    unavailability.
    
    Attributes:
        available: Boolean indicating if GPU monitoring is available
        _initialized: Boolean indicating if NVML was successfully initialized
        
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
        self._initialized = False
        self.available = GPU_AVAILABLE and self._check_gpus()
    
    def _check_gpus(self) -> bool:
        """Check if GPUs are actually available on the system.
        
        Returns:
            True if one or more GPUs are detected, False otherwise.
        """
        if not GPU_AVAILABLE:
            return False
        
        try:
            nvmlInit()
            self._initialized = True
            device_count = nvmlDeviceGetCount()
            return device_count > 0
        except Exception:
            self._initialized = False
            return False
    
    def collect(self) -> Optional[List[Dict[str, Any]]]:
        """Collect current GPU metrics for all available NVIDIA GPUs.
        
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
                    'name': 'NVIDIA GeForce RTX 3050 Laptop GPU',
                    'load': 75.5,
                    'memory_used': 2048.0,
                    'memory_total': 4096.0,
                    'temperature': 65.0
                }
            ]
        """
        if not self.available or not self._initialized:
            return None
        
        try:
            device_count = nvmlDeviceGetCount()
            
            if device_count == 0:
                return None
            
            gpu_data = []
            for i in range(device_count):
                handle = nvmlDeviceGetHandleByIndex(i)
                name = nvmlDeviceGetName(handle)
                
                # Get utilization (GPU and memory)
                utilization = nvmlDeviceGetUtilizationRates(handle)
                
                # Get memory info
                memory = nvmlDeviceGetMemoryInfo(handle)
                
                # Get temperature
                try:
                    temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                except:
                    temp = 0.0
                
                data = {
                    'id': i,
                    'name': name,
                    'load': float(utilization.gpu),  # Already in 0-100 range
                    'memory_used': float(memory.used / (1024 * 1024)),  # Convert bytes to MB
                    'memory_total': float(memory.total / (1024 * 1024)),  # Convert bytes to MB
                    'temperature': float(temp)
                }
                gpu_data.append(data)
                
                # Store the load in history for the first GPU (for graphing)
                if i == 0:
                    self.history.append(data['load'])
            
            self._last_data = gpu_data
            return gpu_data
            
        except Exception:
            return None
    
    def __del__(self):
        """Cleanup: shutdown NVML when monitor is destroyed."""
        if self._initialized:
            try:
                nvmlShutdown()
            except:
                pass
