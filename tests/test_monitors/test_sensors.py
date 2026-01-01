"""Unit tests for SensorsMonitor class.

Tests temperature sensor data collection with graceful fallback when sensors
are unavailable. Mocks psutil.sensors_temperatures() to test various scenarios.
"""

import pytest
from unittest.mock import MagicMock, patch
from collections import namedtuple


# Create a mock for psutil's sensor entry namedtuple
MockSensorEntry = namedtuple('shwtemp', ['label', 'current', 'high', 'critical'])


class TestSensorsMonitor:
    """Test suite for SensorsMonitor class."""
    
    def test_collect_with_sensors_available(self):
        """Test that collect() returns correct data when sensors are available."""
        # Create mock sensor data similar to what psutil returns
        mock_sensors = {
            'coretemp': [
                MockSensorEntry(label='Core 0', current=45.0, high=80.0, critical=100.0),
                MockSensorEntry(label='Core 1', current=47.0, high=80.0, critical=100.0),
                MockSensorEntry(label='Core 2', current=44.0, high=80.0, critical=100.0),
                MockSensorEntry(label='Core 3', current=46.0, high=80.0, critical=100.0),
            ],
            'acpitz': [
                MockSensorEntry(label='temp1', current=50.0, high=None, critical=None),
            ]
        }
        
        # Mock psutil.sensors_temperatures()
        with patch('psutil.sensors_temperatures', return_value=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor and collect data
            monitor = SensorsMonitor(history_size=60)
            
            # Verify monitor is available
            assert monitor.available is True
            
            data = monitor.collect()
            
            # Verify data is not None
            assert data is not None
            assert isinstance(data, dict)
            
            # Verify data structure - should have both sensor types
            assert 'coretemp' in data
            assert 'acpitz' in data
            
            # Check coretemp sensors
            assert len(data['coretemp']) == 4
            core0 = data['coretemp'][0]
            assert core0['label'] == 'Core 0'
            assert core0['current'] == 45.0
            assert core0['high'] == 80.0
            assert core0['critical'] == 100.0
            
            # Check acpitz sensor
            assert len(data['acpitz']) == 1
            acpi = data['acpitz'][0]
            assert acpi['label'] == 'temp1'
            assert acpi['current'] == 50.0
            assert acpi['high'] is None
            assert acpi['critical'] is None
            
            # Verify history was updated with first sensor's temperature
            history = monitor.get_history()
            assert len(history) == 1
            assert history[0] == 45.0  # Core 0 temperature
    
    def test_collect_with_sensors_unavailable_attribute_error(self):
        """Test that collect() returns None when sensors_temperatures() raises AttributeError."""
        # Mock psutil.sensors_temperatures() to raise AttributeError
        with patch('psutil.sensors_temperatures', side_effect=AttributeError):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor
            monitor = SensorsMonitor(history_size=60)
            
            # Verify monitor is not available
            assert monitor.available is False
            
            # Collect data
            data = monitor.collect()
            
            # Verify data is None
            assert data is None
    
    def test_collect_with_empty_sensors_dict(self):
        """Test that collect() handles empty sensors dictionary correctly."""
        # Mock psutil.sensors_temperatures() to return empty dict
        with patch('psutil.sensors_temperatures', return_value={}):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor
            monitor = SensorsMonitor(history_size=60)
            
            # Verify monitor is not available (empty dict = no sensors)
            assert monitor.available is False
            
            # Collect data
            data = monitor.collect()
            
            # Verify data is None
            assert data is None
    
    def test_collect_with_sensors_returning_none(self):
        """Test that collect() handles None return from sensors_temperatures()."""
        # Mock psutil.sensors_temperatures() to return None
        with patch('psutil.sensors_temperatures', return_value=None):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor
            monitor = SensorsMonitor(history_size=60)
            
            # Verify monitor is not available
            assert monitor.available is False
            
            # Collect data
            data = monitor.collect()
            
            # Verify data is None
            assert data is None
    
    def test_collect_with_exception_during_collection(self):
        """Test that collect() returns None when exception occurs during collection."""
        # First call succeeds (for _check_sensors), second call fails
        call_count = [0]
        
        def mock_sensors():
            call_count[0] += 1
            if call_count[0] == 1:
                # First call (during __init__) succeeds
                return {'coretemp': [MockSensorEntry(label='Core 0', current=45.0, 
                                                     high=80.0, critical=100.0)]}
            else:
                # Second call (during collect) fails
                raise Exception("Sensor read error")
        
        with patch('psutil.sensors_temperatures', side_effect=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor
            monitor = SensorsMonitor(history_size=60)
            
            # Monitor should be available during init
            assert monitor.available is True
            
            # But collect should return None due to exception
            data = monitor.collect()
            assert data is None
    
    def test_collect_with_sensor_without_label(self):
        """Test that collect() handles sensors without labels (uses 'N/A')."""
        # Create mock sensor with no label (None)
        mock_sensors = {
            'hwmon0': [
                MockSensorEntry(label=None, current=55.0, high=75.0, critical=90.0),
            ]
        }
        
        with patch('psutil.sensors_temperatures', return_value=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor and collect data
            monitor = SensorsMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify sensor without label gets 'N/A'
            assert data is not None
            assert 'hwmon0' in data
            assert data['hwmon0'][0]['label'] == 'N/A'
            assert data['hwmon0'][0]['current'] == 55.0
    
    def test_collect_multiple_times(self):
        """Test that multiple collect() calls update history correctly."""
        # Create mock sensor data
        # Note: First call is during _check_sensors() in __init__, so we need an extra value
        temps = [45.0, 45.0, 47.0, 46.0, 48.0, 50.0]  # First is for init check
        call_count = [0]
        
        def mock_sensors():
            temp = temps[call_count[0] % len(temps)]
            call_count[0] += 1
            return {
                'coretemp': [
                    MockSensorEntry(label='Core 0', current=temp, high=80.0, critical=100.0)
                ]
            }
        
        with patch('psutil.sensors_temperatures', side_effect=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor (this calls _check_sensors, consuming first temp)
            monitor = SensorsMonitor(history_size=10)
            
            # Collect data multiple times
            expected_temps = [45.0, 47.0, 46.0, 48.0, 50.0]
            for i in range(5):
                data = monitor.collect()
                assert data is not None
                assert data['coretemp'][0]['current'] == expected_temps[i]
            
            # Verify history contains all temperatures
            history = monitor.get_history()
            assert len(history) == 5
            assert history == expected_temps
    
    def test_sensors_with_various_thresholds(self):
        """Test handling of sensors with different threshold configurations."""
        mock_sensors = {
            'sensor1': [
                # All thresholds present
                MockSensorEntry(label='Complete', current=45.0, high=80.0, critical=100.0),
            ],
            'sensor2': [
                # Only high threshold
                MockSensorEntry(label='HighOnly', current=50.0, high=75.0, critical=None),
            ],
            'sensor3': [
                # No thresholds
                MockSensorEntry(label='NoThresholds', current=55.0, high=None, critical=None),
            ],
        }
        
        with patch('psutil.sensors_temperatures', return_value=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor and collect data
            monitor = SensorsMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify all sensors are present with their respective thresholds
            assert data is not None
            
            # Check sensor with all thresholds
            assert data['sensor1'][0]['high'] == 80.0
            assert data['sensor1'][0]['critical'] == 100.0
            
            # Check sensor with only high threshold
            assert data['sensor2'][0]['high'] == 75.0
            assert data['sensor2'][0]['critical'] is None
            
            # Check sensor with no thresholds
            assert data['sensor3'][0]['high'] is None
            assert data['sensor3'][0]['critical'] is None
    
    def test_monitor_becomes_unavailable(self):
        """Test that monitor gracefully handles becoming unavailable after init."""
        # First call succeeds, subsequent calls raise AttributeError
        call_count = [0]
        
        def mock_sensors():
            call_count[0] += 1
            if call_count[0] == 1:
                return {'coretemp': [MockSensorEntry(label='Core 0', current=45.0, 
                                                     high=80.0, critical=100.0)]}
            else:
                raise AttributeError("sensors_temperatures() not available")
        
        with patch('psutil.sensors_temperatures', side_effect=mock_sensors):
            from src.monitors.sensors import SensorsMonitor
            
            # Create monitor - should be available
            monitor = SensorsMonitor(history_size=60)
            assert monitor.available is True
            
            # First collect should fail and update availability
            data = monitor.collect()
            assert data is None
            assert monitor.available is False  # Should update availability
