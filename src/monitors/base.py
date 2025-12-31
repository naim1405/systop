"""Base monitor abstract class for system metric collection.

This module provides the BaseMonitor abstract class that serves as the
foundation for all monitoring modules in systop. Each monitor is responsible
for collecting specific system metrics (CPU, memory, disk, etc.) and maintaining
historical data for visualization.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from src.utils.history import CircularBuffer


class BaseMonitor(ABC):
    """Abstract base class for system monitors.
    
    All monitor implementations must inherit from this class and implement
    the collect() method to gather system metrics. The base class provides
    common functionality for storing historical data and retrieving the most
    recent measurements.
    
    Attributes:
        history: CircularBuffer for storing time-series data points
        _last_data: Dictionary containing the most recent collected metrics
    
    Example:
        class CPUMonitor(BaseMonitor):
            def collect(self) -> Dict[str, Any]:
                data = {"usage": psutil.cpu_percent()}
                self.history.append(data["usage"])
                self._last_data = data
                return data
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize the monitor with a circular buffer for historical data.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60, which represents 60 seconds of data
                         when collecting metrics every second.
        """
        self.history = CircularBuffer(maxsize=history_size)
        self._last_data = None
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect current system metrics.
        
        This method must be implemented by all subclasses. It should:
        1. Gather current system metrics using appropriate libraries (psutil, etc.)
        2. Store relevant numeric values in self.history for time-series visualization
        3. Update self._last_data with the complete collected data
        4. Return the collected data as a dictionary
        
        Returns:
            Dictionary containing the collected metrics. The structure depends
            on the specific monitor implementation, but should be consistent
            across calls for the same monitor type.
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        
        Example:
            return {
                "usage_percent": 45.2,
                "frequency_mhz": 2400.0,
                "temperature_c": 65.0
            }
        """
        pass
    
    def get_history(self) -> list:
        """Return all historical data points.
        
        Returns:
            List of historical values stored in the circular buffer,
            in chronological order (oldest to newest). Returns empty
            list if no data has been collected yet.
        """
        return self.history.get_all()
    
    def get_last_data(self) -> Dict[str, Any]:
        """Return the most recent collected data.
        
        Returns:
            Dictionary containing the most recent metrics from the last
            collect() call, or None if collect() has not been called yet.
        """
        return self._last_data
