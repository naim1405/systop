"""Unit tests for GPUMonitor class.

Tests GPU data collection with graceful fallback when GPU is unavailable.
Mocks GPUtil calls to test both available and unavailable scenarios.
"""

import pytest
import sys
from unittest.mock import MagicMock, patch


class MockGPU:
    """Mock GPU object that mimics GPUtil.GPU structure."""
    
    def __init__(self, id=0, name="NVIDIA GeForce RTX 3080", load=0.75, 
                 memory_used=8192, memory_total=10240, temperature=65.0):
        self.id = id
        self.name = name
        self.load = load  # 0-1 range
        self.memoryUsed = memory_used
        self.memoryTotal = memory_total
        self.temperature = temperature


class TestGPUMonitor:
    """Test suite for GPUMonitor class."""
    
    def test_collect_with_gpu_available(self):
        """Test that collect() returns correct data when GPU is available."""
        # Setup mock GPUtil module
        mock_gputil = MagicMock()
        mock_gpu = MockGPU(
            id=0,
            name="NVIDIA GeForce RTX 3080",
            load=0.755,  # 75.5%
            memory_used=8192.0,
            memory_total=10240.0,
            temperature=65.0
        )
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        # Mock the module import
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            # Import after mocking
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            # Create monitor and collect data
            monitor = gpu_module.GPUMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify data is not None
            assert data is not None
            assert isinstance(data, list)
            assert len(data) == 1
            
            # Verify data structure
            gpu_data = data[0]
            assert 'id' in gpu_data
            assert 'name' in gpu_data
            assert 'load' in gpu_data
            assert 'memory_used' in gpu_data
            assert 'memory_total' in gpu_data
            assert 'temperature' in gpu_data
            
            # Verify data types
            assert isinstance(gpu_data['id'], int)
            assert isinstance(gpu_data['name'], str)
            assert isinstance(gpu_data['load'], float)
            assert isinstance(gpu_data['memory_used'], (int, float))
            assert isinstance(gpu_data['memory_total'], (int, float))
            assert isinstance(gpu_data['temperature'], float)
            
            # Verify values
            assert gpu_data['id'] == 0
            assert gpu_data['name'] == "NVIDIA GeForce RTX 3080"
            assert gpu_data['load'] == 75.5  # Converted from 0.755 to percentage
            assert gpu_data['memory_used'] == 8192.0
            assert gpu_data['memory_total'] == 10240.0
            assert gpu_data['temperature'] == 65.0
    
    def test_collect_with_multiple_gpus(self):
        """Test that collect() handles multiple GPUs correctly."""
        # Setup mocks for two GPUs
        mock_gputil = MagicMock()
        mock_gpu1 = MockGPU(id=0, name="GPU 1", load=0.50, 
                           memory_used=4096, memory_total=8192, temperature=60.0)
        mock_gpu2 = MockGPU(id=1, name="GPU 2", load=0.80,
                           memory_used=6144, memory_total=8192, temperature=70.0)
        mock_gputil.getGPUs.return_value = [mock_gpu1, mock_gpu2]
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            # Create monitor and collect data
            monitor = gpu_module.GPUMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify data
            assert data is not None
            assert len(data) == 2
            assert data[0]['id'] == 0
            assert data[0]['name'] == "GPU 1"
            assert data[0]['load'] == 50.0
            assert data[1]['id'] == 1
            assert data[1]['name'] == "GPU 2"
            assert data[1]['load'] == 80.0
    
    def test_collect_stores_history(self):
        """Test that collect() stores GPU load in history for first GPU."""
        mock_gputil = MagicMock()
        mock_gpu = MockGPU(load=0.65)  # 65%
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=60)
            
            # Collect data multiple times
            monitor.collect()
            monitor.collect()
            monitor.collect()
            
            # Verify history
            history = monitor.get_history()
            assert len(history) == 3
            assert all(load == 65.0 for load in history)
    
    def test_collect_with_no_gpus_detected(self):
        """Test that collect() returns None when no GPUs are detected."""
        # Empty GPU list
        mock_gputil = MagicMock()
        mock_gputil.getGPUs.return_value = []
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify None is returned
            assert data is None
            assert not monitor.available
    
    def test_collect_with_gputil_not_available(self):
        """Test that collect() returns None when GPUtil is not installed."""
        # Simulate ImportError by removing GPUtil from modules and reloading
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'GPUtil':
                raise ImportError("No module named 'GPUtil'")
            return original_import(name, *args, **kwargs)
        
        # Remove module from cache
        sys.modules.pop('GPUtil', None)
        sys.modules.pop('src.monitors.gpu', None)
        
        with patch('builtins.__import__', side_effect=mock_import):
            import src.monitors.gpu as gpu_module
            from importlib import reload
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=60)
            data = monitor.collect()
            
            # Verify None is returned
            assert data is None
            assert not monitor.available
    
    def test_collect_handles_exception(self):
        """Test that collect() returns None when GPUtil raises an exception."""
        # Setup mock to raise exception during initialization
        mock_gputil = MagicMock()
        mock_gputil.getGPUs.side_effect = Exception("GPU access error")
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=60)
            
            # Monitor should not be available due to exception during check
            assert not monitor.available
            
            # Collect should return None
            data = monitor.collect()
            assert data is None
    
    def test_collect_exception_during_data_collection(self):
        """Test that collect() returns None when exception occurs during collection."""
        # First call succeeds (for initialization), second call fails
        mock_gputil = MagicMock()
        mock_gpu = MockGPU()
        call_count = [0]
        
        def side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return [mock_gpu]  # Initialization check
            else:
                raise Exception("Runtime error")  # During collect()
        
        mock_gputil.getGPUs.side_effect = side_effect
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=60)
            assert monitor.available  # Should be available after init
            
            data = monitor.collect()
            assert data is None  # Should return None on exception
    
    def test_monitor_availability_check(self):
        """Test that monitor correctly checks GPU availability on init."""
        mock_gputil = MagicMock()
        mock_gpu = MockGPU()
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor()
            
            # Verify monitor is marked as available
            assert monitor.available
    
    def test_get_last_data(self):
        """Test that get_last_data() returns the most recent collection."""
        mock_gputil = MagicMock()
        mock_gpu = MockGPU(load=0.75)
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor()
            data = monitor.collect()
            
            # Get last data
            last_data = monitor.get_last_data()
            
            # Verify it matches the collected data
            assert last_data == data
            assert last_data[0]['load'] == 75.0
    
    def test_history_size_limit(self):
        """Test that history respects the size limit."""
        mock_gputil = MagicMock()
        mock_gpu = MockGPU(load=0.50)
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        with patch.dict(sys.modules, {'GPUtil': mock_gputil}):
            from importlib import reload
            import src.monitors.gpu as gpu_module
            reload(gpu_module)
            
            monitor = gpu_module.GPUMonitor(history_size=5)
            
            # Collect more data than history size
            for i in range(10):
                monitor.collect()
            
            # Verify history is limited to 5
            history = monitor.get_history()
            assert len(history) == 5
