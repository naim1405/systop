"""Unit tests for GPUMonitor class.

Tests GPU data collection with graceful fallback when GPU is unavailable.
Mocks pynvml calls to test both available and unavailable scenarios.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestGPUMonitor:
    """Test suite for GPUMonitor class."""
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlDeviceGetHandleByIndex')
    @patch('src.monitors.gpu.nvmlDeviceGetName')
    @patch('src.monitors.gpu.nvmlDeviceGetUtilizationRates')
    @patch('src.monitors.gpu.nvmlDeviceGetMemoryInfo')
    @patch('src.monitors.gpu.nvmlDeviceGetTemperature')
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_with_gpu_available(
        self,
        mock_init,
        mock_temp,
        mock_memory,
        mock_util,
        mock_name,
        mock_handle,
        mock_count
    ):
        """Test that collect() returns correct data when GPU is available."""
        # Setup mocks
        mock_count.return_value = 1
        mock_handle.return_value = MagicMock()
        mock_name.return_value = "NVIDIA GeForce RTX 3080"
        
        # Mock utilization (already in 0-100 range)
        util_mock = MagicMock()
        util_mock.gpu = 75.5
        util_mock.memory = 80.0
        mock_util.return_value = util_mock
        
        # Mock memory (in bytes)
        mem_mock = MagicMock()
        mem_mock.used = 8192 * 1024 * 1024  # 8192 MB in bytes
        mem_mock.total = 10240 * 1024 * 1024  # 10240 MB in bytes
        mock_memory.return_value = mem_mock
        
        # Mock temperature
        mock_temp.return_value = 65.0
        
        # Create monitor and collect data
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
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
        assert gpu_data['load'] == 75.5
        assert gpu_data['memory_used'] == 8192.0
        assert gpu_data['memory_total'] == 10240.0
        assert gpu_data['temperature'] == 65.0
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlDeviceGetHandleByIndex')
    @patch('src.monitors.gpu.nvmlDeviceGetName')
    @patch('src.monitors.gpu.nvmlDeviceGetUtilizationRates')
    @patch('src.monitors.gpu.nvmlDeviceGetMemoryInfo')
    @patch('src.monitors.gpu.nvmlDeviceGetTemperature')
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_with_multiple_gpus(
        self,
        mock_init,
        mock_temp,
        mock_memory,
        mock_util,
        mock_name,
        mock_handle,
        mock_count
    ):
        """Test that collect() handles multiple GPUs correctly."""
        # Setup mocks for two GPUs
        mock_count.return_value = 2
        mock_handle.side_effect = [MagicMock(), MagicMock()]
        mock_name.side_effect = ["GPU 1", "GPU 2"]
        
        # Mock utilization
        util_mock1 = MagicMock()
        util_mock1.gpu = 50.0
        util_mock2 = MagicMock()
        util_mock2.gpu = 80.0
        mock_util.side_effect = [util_mock1, util_mock2]
        
        # Mock memory
        mem_mock1 = MagicMock()
        mem_mock1.used = 4096 * 1024 * 1024
        mem_mock1.total = 8192 * 1024 * 1024
        mem_mock2 = MagicMock()
        mem_mock2.used = 6144 * 1024 * 1024
        mem_mock2.total = 8192 * 1024 * 1024
        mock_memory.side_effect = [mem_mock1, mem_mock2]
        
        # Mock temperature
        mock_temp.side_effect = [60.0, 70.0]
        
        # Create monitor and collect data
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
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
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlDeviceGetHandleByIndex')
    @patch('src.monitors.gpu.nvmlDeviceGetName')
    @patch('src.monitors.gpu.nvmlDeviceGetUtilizationRates')
    @patch('src.monitors.gpu.nvmlDeviceGetMemoryInfo')
    @patch('src.monitors.gpu.nvmlDeviceGetTemperature')
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_stores_history(
        self,
        mock_init,
        mock_temp,
        mock_memory,
        mock_util,
        mock_name,
        mock_handle,
        mock_count
    ):
        """Test that collect() stores GPU load in history for first GPU."""
        # Setup mocks
        mock_count.return_value = 1
        mock_handle.return_value = MagicMock()
        mock_name.return_value = "GPU"
        
        util_mock = MagicMock()
        util_mock.gpu = 65.0
        mock_util.return_value = util_mock
        
        mem_mock = MagicMock()
        mem_mock.used = 1024 * 1024 * 1024
        mem_mock.total = 4096 * 1024 * 1024
        mock_memory.return_value = mem_mock
        
        mock_temp.return_value = 60.0
        
        # Create monitor and collect multiple times
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
        monitor.collect()
        monitor.collect()
        monitor.collect()
        
        # Verify history
        history = monitor.get_history()
        assert len(history) == 3
        assert all(load == 65.0 for load in history)
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_with_no_gpus_detected(
        self,
        mock_init,
        mock_count
    ):
        """Test that collect() returns None when no GPUs are detected."""
        # Empty GPU list
        mock_count.return_value = 0
        
        # Create monitor and collect
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify None is returned
        assert data is None
        assert not monitor.available
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', False)
    def test_collect_with_gputil_not_available(self):
        """Test that collect() returns None when pynvml is not installed."""
        # Create monitor when GPU_AVAILABLE is False
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify None is returned
        assert data is None
        assert not monitor.available
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_handles_exception(self, mock_init):
        """Test that collect() returns None when pynvml raises an exception."""
        # Setup mock to raise exception during initialization
        mock_init.side_effect = Exception("GPU access error")
        
        # Create monitor
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=60)
        
        # Monitor should not be available due to exception during check
        assert not monitor.available
        
        # Collect should return None
        data = monitor.collect()
        assert data is None
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlInit')
    def test_collect_exception_during_data_collection(
        self,
        mock_init,
        mock_count
    ):
        """Test that collect() returns None when exception occurs during collection."""
        # First call succeeds (for initialization), second call fails
        call_count = [0]
        
        def side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return 1  # Initialization check
            else:
                raise Exception("Runtime error")  # During collect()
        
        mock_count.side_effect = side_effect
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlInit')
    def test_monitor_availability_check(
        self,
        mock_init,
        mock_count
    ):
        """Test that monitor correctly checks GPU availability on init."""
        mock_count.return_value = 1
        
        # Create monitor
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor()
        
        # Verify monitor is marked as available
        assert monitor.available
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlDeviceGetHandleByIndex')
    @patch('src.monitors.gpu.nvmlDeviceGetName')
    @patch('src.monitors.gpu.nvmlDeviceGetUtilizationRates')
    @patch('src.monitors.gpu.nvmlDeviceGetMemoryInfo')
    @patch('src.monitors.gpu.nvmlDeviceGetTemperature')
    @patch('src.monitors.gpu.nvmlInit')
    def test_get_last_data(
        self,
        mock_init,
        mock_temp,
        mock_memory,
        mock_util,
        mock_name,
        mock_handle,
        mock_count
    ):
        """Test that get_last_data() returns the most recent collection."""
        # Setup mocks
        mock_count.return_value = 1
        mock_handle.return_value = MagicMock()
        mock_name.return_value = "GPU"
        
        util_mock = MagicMock()
        util_mock.gpu = 75.0
        mock_util.return_value = util_mock
        
        mem_mock = MagicMock()
        mem_mock.used = 1024 * 1024 * 1024
        mem_mock.total = 4096 * 1024 * 1024
        mock_memory.return_value = mem_mock
        
        mock_temp.return_value = 60.0
        
        # Create monitor and collect
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor()
        data = monitor.collect()
        
        # Get last data
        last_data = monitor.get_last_data()
        
        # Verify it matches the collected data
        assert last_data == data
        assert last_data[0]['load'] == 75.0
    
    @patch('src.monitors.gpu.GPU_AVAILABLE', True)
    @patch('src.monitors.gpu.nvmlDeviceGetCount')
    @patch('src.monitors.gpu.nvmlDeviceGetHandleByIndex')
    @patch('src.monitors.gpu.nvmlDeviceGetName')
    @patch('src.monitors.gpu.nvmlDeviceGetUtilizationRates')
    @patch('src.monitors.gpu.nvmlDeviceGetMemoryInfo')
    @patch('src.monitors.gpu.nvmlDeviceGetTemperature')
    @patch('src.monitors.gpu.nvmlInit')
    def test_history_size_limit(
        self,
        mock_init,
        mock_temp,
        mock_memory,
        mock_util,
        mock_name,
        mock_handle,
        mock_count
    ):
        """Test that history respects the size limit."""
        # Setup mocks
        mock_count.return_value = 1
        mock_handle.return_value = MagicMock()
        mock_name.return_value = "GPU"
        
        util_mock = MagicMock()
        util_mock.gpu = 50.0
        mock_util.return_value = util_mock
        
        mem_mock = MagicMock()
        mem_mock.used = 1024 * 1024 * 1024
        mem_mock.total = 4096 * 1024 * 1024
        mock_memory.return_value = mem_mock
        
        mock_temp.return_value = 60.0
        
        # Create monitor with small history
        from src.monitors.gpu import GPUMonitor
        monitor = GPUMonitor(history_size=5)
        
        # Collect more data than history size
        for i in range(10):
            monitor.collect()
        
        # Verify history is limited to 5
        history = monitor.get_history()
        assert len(history) == 5

