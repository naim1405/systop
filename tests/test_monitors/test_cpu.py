"""Unit tests for CPUMonitor class.

Tests CPU data collection, history tracking, and data structure validation
using mocked psutil and cpuinfo calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.monitors.cpu import CPUMonitor


class TestCPUMonitor:
    """Test suite for CPUMonitor class."""
    
    @pytest.fixture
    def mock_cpu_info(self):
        """Mock cpuinfo data."""
        return {
            'brand_raw': 'Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz',
            'hz_advertised': [1800000000, 0],
            'arch': 'X86_64',
            'bits': 64,
            'count': 8
        }
    
    @pytest.fixture
    def mock_cpu_freq(self):
        """Mock CPU frequency data."""
        freq = MagicMock()
        freq.current = 2400.0
        freq.min = 800.0
        freq.max = 4000.0
        return freq
    
    @pytest.fixture
    def mock_load_avg(self):
        """Mock load average data."""
        return (1.5, 1.2, 0.9)
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    @patch('src.monitors.cpu.psutil.cpu_percent')
    @patch('src.monitors.cpu.psutil.cpu_freq')
    @patch('src.monitors.cpu.psutil.cpu_count')
    @patch('src.monitors.cpu.os.getloadavg')
    def test_collect_returns_correct_structure(
        self, 
        mock_getloadavg, 
        mock_cpu_count, 
        mock_freq, 
        mock_cpu_percent, 
        mock_get_cpu_info,
        mock_cpu_info,
        mock_cpu_freq,
        mock_load_avg
    ):
        """Test that collect() returns the correct data structure."""
        # Setup mocks
        mock_get_cpu_info.return_value = mock_cpu_info
        mock_cpu_percent.side_effect = [
            45.5,  # overall percent (first call)
            [40.0, 50.0, 45.0, 48.0]  # per-core percents (second call with percpu=True)
        ]
        mock_freq.return_value = mock_cpu_freq
        mock_cpu_count.side_effect = [4, 8]  # physical, then logical
        mock_getloadavg.return_value = mock_load_avg
        
        # Create monitor and collect data
        monitor = CPUMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify data structure
        assert 'overall_percent' in data
        assert 'per_core_percent' in data
        assert 'frequency' in data
        assert 'load_avg' in data
        assert 'cpu_count' in data
        assert 'model' in data
        
        # Verify data types
        assert isinstance(data['overall_percent'], float)
        assert isinstance(data['per_core_percent'], list)
        assert isinstance(data['frequency'], dict)
        assert isinstance(data['load_avg'], dict)
        assert isinstance(data['cpu_count'], dict)
        assert isinstance(data['model'], str)
        
        # Verify values
        assert data['overall_percent'] == 45.5
        assert data['per_core_percent'] == [40.0, 50.0, 45.0, 48.0]
        assert data['frequency']['current'] == 2400.0
        assert data['frequency']['min'] == 800.0
        assert data['frequency']['max'] == 4000.0
        assert data['load_avg']['1min'] == 1.5
        assert data['load_avg']['5min'] == 1.2
        assert data['load_avg']['15min'] == 0.9
        assert data['cpu_count']['physical'] == 4
        assert data['cpu_count']['logical'] == 8
        assert data['model'] == 'Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz'
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    @patch('src.monitors.cpu.psutil.cpu_percent')
    @patch('src.monitors.cpu.psutil.cpu_freq')
    @patch('src.monitors.cpu.psutil.cpu_count')
    @patch('src.monitors.cpu.os.getloadavg')
    def test_history_is_populated(
        self, 
        mock_getloadavg, 
        mock_cpu_count, 
        mock_freq, 
        mock_cpu_percent, 
        mock_get_cpu_info,
        mock_cpu_info,
        mock_cpu_freq,
        mock_load_avg
    ):
        """Test that overall CPU percentage is stored in history."""
        # Setup mocks
        mock_get_cpu_info.return_value = mock_cpu_info
        mock_cpu_percent.side_effect = [25.0, [20.0, 30.0], 35.0, [30.0, 40.0], 45.0, [40.0, 50.0]]
        mock_freq.return_value = mock_cpu_freq
        mock_cpu_count.side_effect = [2, 4, 2, 4, 2, 4]
        mock_getloadavg.return_value = mock_load_avg
        
        # Create monitor
        monitor = CPUMonitor(history_size=10)
        
        # Collect multiple times
        monitor.collect()
        monitor.collect()
        monitor.collect()
        
        # Check history
        history = monitor.get_history()
        assert len(history) == 3
        assert history[0] == 25.0
        assert history[1] == 35.0
        assert history[2] == 45.0
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    @patch('src.monitors.cpu.psutil.cpu_percent')
    @patch('src.monitors.cpu.psutil.cpu_freq')
    @patch('src.monitors.cpu.psutil.cpu_count')
    @patch('src.monitors.cpu.os.getloadavg')
    def test_last_data_is_stored(
        self, 
        mock_getloadavg, 
        mock_cpu_count, 
        mock_freq, 
        mock_cpu_percent, 
        mock_get_cpu_info,
        mock_cpu_info,
        mock_cpu_freq,
        mock_load_avg
    ):
        """Test that _last_data is updated after collection."""
        # Setup mocks
        mock_get_cpu_info.return_value = mock_cpu_info
        mock_cpu_percent.side_effect = [50.0, [45.0, 55.0]]
        mock_freq.return_value = mock_cpu_freq
        mock_cpu_count.side_effect = [2, 4]
        mock_getloadavg.return_value = mock_load_avg
        
        # Create monitor and collect
        monitor = CPUMonitor()
        data = monitor.collect()
        
        # Verify last_data is set
        last_data = monitor.get_last_data()
        assert last_data is not None
        assert last_data == data
        assert last_data['overall_percent'] == 50.0
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    @patch('src.monitors.cpu.psutil.cpu_percent')
    @patch('src.monitors.cpu.psutil.cpu_freq')
    @patch('src.monitors.cpu.psutil.cpu_count')
    @patch('src.monitors.cpu.os.getloadavg')
    def test_handles_missing_frequency(
        self, 
        mock_getloadavg, 
        mock_cpu_count, 
        mock_freq, 
        mock_cpu_percent, 
        mock_get_cpu_info,
        mock_cpu_info,
        mock_load_avg
    ):
        """Test handling when CPU frequency is not available."""
        # Setup mocks
        mock_get_cpu_info.return_value = mock_cpu_info
        mock_cpu_percent.side_effect = [30.0, [25.0, 35.0]]
        mock_freq.return_value = None  # Frequency not available
        mock_cpu_count.side_effect = [2, 4]
        mock_getloadavg.return_value = mock_load_avg
        
        # Create monitor and collect
        monitor = CPUMonitor()
        data = monitor.collect()
        
        # Verify frequency defaults to 0
        assert data['frequency']['current'] == 0.0
        assert data['frequency']['min'] == 0.0
        assert data['frequency']['max'] == 0.0
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    @patch('src.monitors.cpu.psutil.cpu_percent')
    @patch('src.monitors.cpu.psutil.cpu_freq')
    @patch('src.monitors.cpu.psutil.cpu_count')
    @patch('src.monitors.cpu.os.getloadavg')
    def test_handles_different_core_counts(
        self, 
        mock_getloadavg, 
        mock_cpu_count, 
        mock_freq, 
        mock_cpu_percent, 
        mock_get_cpu_info,
        mock_cpu_info,
        mock_cpu_freq,
        mock_load_avg
    ):
        """Test with various CPU core configurations."""
        # Setup mocks - single core
        mock_get_cpu_info.return_value = {'brand_raw': 'Single Core CPU'}
        mock_cpu_percent.side_effect = [10.0, [10.0]]
        mock_freq.return_value = mock_cpu_freq
        mock_cpu_count.side_effect = [1, 1]
        mock_getloadavg.return_value = mock_load_avg
        
        # Test single core
        monitor = CPUMonitor()
        data = monitor.collect()
        assert data['cpu_count']['physical'] == 1
        assert data['cpu_count']['logical'] == 1
        assert len(data['per_core_percent']) == 1
        
        # Setup mocks - many cores
        mock_cpu_percent.side_effect = [
            50.0, 
            [45.0, 48.0, 52.0, 50.0, 51.0, 49.0, 53.0, 47.0,
             46.0, 50.0, 51.0, 52.0, 48.0, 49.0, 54.0, 46.0]
        ]
        mock_cpu_count.side_effect = [8, 16]
        mock_get_cpu_info.return_value = {'brand_raw': 'AMD Ryzen 9 5950X'}
        
        # Test many cores
        monitor2 = CPUMonitor()
        data2 = monitor2.collect()
        assert data2['cpu_count']['physical'] == 8
        assert data2['cpu_count']['logical'] == 16
        assert len(data2['per_core_percent']) == 16
    
    @patch('src.monitors.cpu.cpuinfo.get_cpu_info')
    def test_cpu_info_extraction(self, mock_get_cpu_info):
        """Test CPU model name extraction from cpuinfo."""
        # Test with brand_raw
        mock_get_cpu_info.return_value = {'brand_raw': 'Test CPU Brand'}
        monitor = CPUMonitor()
        assert monitor._cpu_info.get('brand_raw') == 'Test CPU Brand'
        
        # Test without brand_raw
        mock_get_cpu_info.return_value = {}
        monitor2 = CPUMonitor()
        # The monitor should have stored the empty dict
        assert monitor2._cpu_info == {}
