"""Temperature sensors monitoring module for collecting sensor data with graceful fallback.

This module provides the SensorsMonitor class that collects temperature sensor data
including CPU, GPU, and other hardware temperatures using psutil.sensors_temperatures().
If sensors are not available (e.g., on VMs or systems without sensor support), it 
gracefully returns None to allow the application to hide the widget instead of crashing.

Note: Sensor availability varies by system. VMs and some hardware may not expose sensors.
"""

import psutil
from typing import Dict, List, Any, Optional
from src.monitors.base import BaseMonitor


class SensorsMonitor(BaseMonitor):
    """Monitor for temperature sensors with graceful fallback.
    
    Collects temperature data from all available hardware sensors using psutil.
    If sensors are not available or accessible, returns None to indicate 
    unavailability, allowing the UI to hide the sensors widget.
    
    Attributes:
        available: Boolean indicating if temperature sensors are available
        
    Example:
        monitor = SensorsMonitor()
        data = monitor.collect()
        if data is None:
            print("Sensors: Not available")
        else:
            for sensor_type, sensors in data.items():
                print(f"{sensor_type}: {sensors[0].current}°C")
    """
    
    def __init__(self, history_size: int = 60):
        """Initialize sensors monitor and check sensor availability.
        
        Args:
            history_size: Maximum number of data points to store in history.
                         Default is 60 for one minute of per-5-second data.
        """
        super().__init__(history_size)
        self.available = self._check_sensors()
    
    def _check_sensors(self) -> bool:
        """Check if temperature sensors are available on the system.
        
        Returns:
            True if one or more temperature sensors are detected, False otherwise.
        """
        try:
            temps = psutil.sensors_temperatures()
            return temps is not None and len(temps) > 0
        except AttributeError:
            # sensors_temperatures() not available on this platform
            return False
        except Exception:
            # Any other error means sensors are not accessible
            return False
    
    def collect(self) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """Collect current temperature sensor readings from all available sensors.
        
        Returns None if sensors are not available or an error occurs.
        Otherwise returns a dictionary grouped by sensor type (e.g., 'coretemp', 
        'acpitz', etc.) with each containing a list of sensor readings.
        
        Returns:
            None if sensors unavailable, otherwise dictionary like:
            {
                'coretemp': [
                    {
                        'label': 'Core 0',
                        'current': 45.0,
                        'high': 80.0,
                        'critical': 100.0
                    },
                    ...
                ],
                'acpitz': [
                    {
                        'label': 'temp1',
                        'current': 50.0,
                        'high': None,
                        'critical': None
                    }
                ]
            }
                
        Example:
            data = monitor.collect()
            if data:
                for sensor_type, readings in data.items():
                    for reading in readings:
                        print(f"{reading['label']}: {reading['current']}°C")
        """
        if not self.available:
            return None
        
        try:
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return None
            
            # Convert psutil's namedtuple format to dictionary format
            result = {}
            for sensor_type, sensors in temps.items():
                result[sensor_type] = []
                for sensor in sensors:
                    result[sensor_type].append({
                        'label': sensor.label or 'N/A',
                        'current': sensor.current,
                        'high': sensor.high,
                        'critical': sensor.critical
                    })
            
            # Store the first sensor's current temperature in history (for potential graphing)
            if result:
                first_type = next(iter(result))
                if result[first_type]:
                    self.history.append(result[first_type][0]['current'])
            
            self._last_data = result
            return result
            
        except AttributeError:
            # sensors_temperatures() not available
            self.available = False
            return None
        except Exception:
            # Any other error
            return None
