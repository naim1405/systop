"""Unit tests for MemoryMonitor class.

Tests memory data collection, history tracking, and data structure validation
using mocked psutil calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.monitors.memory import MemoryMonitor


class TestMemoryMonitor:
    """Test suite for MemoryMonitor class."""
    
    @pytest.fixture
    def mock_virtual_memory(self):
        """Mock virtual memory data."""
        vm = MagicMock()
        vm.total = 16777216000  # ~16GB
        vm.available = 8388608000  # ~8GB
        vm.used = 8388608000  # ~8GB
        vm.free = 2097152000  # ~2GB
        vm.percent = 50.0
        return vm
    
    @pytest.fixture
    def mock_swap_memory(self):
        """Mock swap memory data."""
        swap = MagicMock()
        swap.total = 4194304000  # ~4GB
        swap.used = 1048576000  # ~1GB
        swap.free = 3145728000  # ~3GB
        swap.percent = 25.0
        return swap
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_collect_returns_correct_structure(
        self, 
        mock_swap_mem, 
        mock_virtual_mem,
        mock_virtual_memory,
        mock_swap_memory
    ):
        """Test that collect() returns the correct data structure."""
        # Setup mocks
        mock_virtual_mem.return_value = mock_virtual_memory
        mock_swap_mem.return_value = mock_swap_memory
        
        # Create monitor and collect data
        monitor = MemoryMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify data structure
        assert 'ram' in data
        assert 'swap' in data
        
        # Verify RAM structure
        assert 'total' in data['ram']
        assert 'available' in data['ram']
        assert 'used' in data['ram']
        assert 'free' in data['ram']
        assert 'percent' in data['ram']
        
        # Verify swap structure
        assert 'total' in data['swap']
        assert 'used' in data['swap']
        assert 'free' in data['swap']
        assert 'percent' in data['swap']
        
        # Verify data types
        assert isinstance(data['ram']['total'], int)
        assert isinstance(data['ram']['available'], int)
        assert isinstance(data['ram']['used'], int)
        assert isinstance(data['ram']['free'], int)
        assert isinstance(data['ram']['percent'], float)
        
        assert isinstance(data['swap']['total'], int)
        assert isinstance(data['swap']['used'], int)
        assert isinstance(data['swap']['free'], int)
        assert isinstance(data['swap']['percent'], float)
        
        # Verify values
        assert data['ram']['total'] == 16777216000
        assert data['ram']['available'] == 8388608000
        assert data['ram']['used'] == 8388608000
        assert data['ram']['free'] == 2097152000
        assert data['ram']['percent'] == 50.0
        
        assert data['swap']['total'] == 4194304000
        assert data['swap']['used'] == 1048576000
        assert data['swap']['free'] == 3145728000
        assert data['swap']['percent'] == 25.0
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_history_populated(
        self, 
        mock_swap_mem, 
        mock_virtual_mem,
        mock_virtual_memory,
        mock_swap_memory
    ):
        """Test that RAM percent is stored in history after collect()."""
        # Setup mocks
        mock_virtual_mem.return_value = mock_virtual_memory
        mock_swap_mem.return_value = mock_swap_memory
        
        # Create monitor and collect data
        monitor = MemoryMonitor(history_size=60)
        
        # History should be empty initially
        assert len(monitor.get_history()) == 0
        
        # Collect data
        data = monitor.collect()
        
        # History should now have one entry
        history = monitor.get_history()
        assert len(history) == 1
        assert history[0] == 50.0
        assert history[0] == data['ram']['percent']
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_multiple_collections_populate_history(
        self, 
        mock_swap_mem, 
        mock_virtual_mem
    ):
        """Test that multiple collect() calls populate history correctly."""
        # Create monitor
        monitor = MemoryMonitor(history_size=60)
        
        # Collect multiple times with different values
        percentages = [45.0, 50.5, 55.2, 60.1, 48.7]
        
        for percent in percentages:
            vm = MagicMock()
            vm.total = 16777216000
            vm.available = 8388608000
            vm.used = 8388608000
            vm.free = 2097152000
            vm.percent = percent
            
            swap = MagicMock()
            swap.total = 4194304000
            swap.used = 1048576000
            swap.free = 3145728000
            swap.percent = 25.0
            
            mock_virtual_mem.return_value = vm
            mock_swap_mem.return_value = swap
            
            monitor.collect()
        
        # Verify history length and values
        history = monitor.get_history()
        assert len(history) == 5
        assert history == percentages
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_last_data_updated(
        self, 
        mock_swap_mem, 
        mock_virtual_mem,
        mock_virtual_memory,
        mock_swap_memory
    ):
        """Test that _last_data is updated after collect()."""
        # Setup mocks
        mock_virtual_mem.return_value = mock_virtual_memory
        mock_swap_mem.return_value = mock_swap_memory
        
        # Create monitor
        monitor = MemoryMonitor(history_size=60)
        
        # Initially should be None
        assert monitor.get_last_data() is None
        
        # Collect data
        data = monitor.collect()
        
        # last_data should match collected data
        last_data = monitor.get_last_data()
        assert last_data is not None
        assert last_data == data
        assert last_data['ram']['percent'] == 50.0
        assert last_data['swap']['percent'] == 25.0
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_no_swap_configured(
        self, 
        mock_swap_mem, 
        mock_virtual_mem,
        mock_virtual_memory
    ):
        """Test handling of system with no swap configured."""
        # Setup mocks
        mock_virtual_mem.return_value = mock_virtual_memory
        
        # Mock no swap
        swap = MagicMock()
        swap.total = 0
        swap.used = 0
        swap.free = 0
        swap.percent = 0.0
        mock_swap_mem.return_value = swap
        
        # Create monitor and collect data
        monitor = MemoryMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify swap data is zero
        assert data['swap']['total'] == 0
        assert data['swap']['used'] == 0
        assert data['swap']['free'] == 0
        assert data['swap']['percent'] == 0.0
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_history_size_limit(
        self, 
        mock_swap_mem, 
        mock_virtual_mem
    ):
        """Test that history respects the size limit."""
        # Create monitor with small history size
        monitor = MemoryMonitor(history_size=5)
        
        # Collect more than history_size times
        for i in range(10):
            vm = MagicMock()
            vm.total = 16777216000
            vm.available = 8388608000
            vm.used = 8388608000
            vm.free = 2097152000
            vm.percent = float(i * 10)
            
            swap = MagicMock()
            swap.total = 4194304000
            swap.used = 1048576000
            swap.free = 3145728000
            swap.percent = 25.0
            
            mock_virtual_mem.return_value = vm
            mock_swap_mem.return_value = swap
            
            monitor.collect()
        
        # History should only have the last 5 values
        history = monitor.get_history()
        assert len(history) == 5
        assert history == [50.0, 60.0, 70.0, 80.0, 90.0]
    
    @patch('src.monitors.memory.psutil.virtual_memory')
    @patch('src.monitors.memory.psutil.swap_memory')
    def test_high_memory_usage(
        self, 
        mock_swap_mem, 
        mock_virtual_mem
    ):
        """Test handling of high memory usage (>90%)."""
        # Mock high memory usage
        vm = MagicMock()
        vm.total = 16777216000
        vm.available = 1677721600  # Only 10% available
        vm.used = 15099494400  # 90% used
        vm.free = 1677721600
        vm.percent = 90.0
        
        swap = MagicMock()
        swap.total = 4194304000
        swap.used = 3774873600  # 90% used
        swap.free = 419430400
        swap.percent = 90.0
        
        mock_virtual_mem.return_value = vm
        mock_swap_mem.return_value = swap
        
        # Create monitor and collect data
        monitor = MemoryMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify high usage is correctly reported
        assert data['ram']['percent'] == 90.0
        assert data['swap']['percent'] == 90.0
        
        # Verify history
        history = monitor.get_history()
        assert len(history) == 1
        assert history[0] == 90.0
