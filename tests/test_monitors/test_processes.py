"""Unit tests for ProcessMonitor class.

Tests process data collection, sorting, filtering, and kill functionality
using mocked psutil calls.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from src.monitors.processes import ProcessMonitor


class TestProcessMonitor:
    """Test suite for ProcessMonitor class."""
    
    @pytest.fixture
    def mock_process_list(self):
        """Mock list of processes with various attributes."""
        # Create mock process objects
        processes = []
        
        # Process 1: High CPU, medium memory
        p1 = MagicMock()
        p1.info = {
            'pid': 1234,
            'name': 'python',
            'username': 'user1',
            'cpu_percent': 75.5,
            'memory_percent': 5.2,
            'memory_info': MagicMock(rss=100 * 1024 * 1024),  # 100 MB
            'status': 'running',
            'create_time': 1704067200.0
        }
        processes.append(p1)
        
        # Process 2: Low CPU, high memory
        p2 = MagicMock()
        p2.info = {
            'pid': 5678,
            'name': 'chrome',
            'username': 'user1',
            'cpu_percent': 2.1,
            'memory_percent': 15.8,
            'memory_info': MagicMock(rss=500 * 1024 * 1024),  # 500 MB
            'status': 'sleeping',
            'create_time': 1704060000.0
        }
        processes.append(p2)
        
        # Process 3: Medium CPU, low memory
        p3 = MagicMock()
        p3.info = {
            'pid': 9012,
            'name': 'systemd',
            'username': 'root',
            'cpu_percent': 10.0,
            'memory_percent': 0.5,
            'memory_info': MagicMock(rss=10 * 1024 * 1024),  # 10 MB
            'status': 'sleeping',
            'create_time': 1704050000.0
        }
        processes.append(p3)
        
        # Process 4: Zero CPU, zero memory
        p4 = MagicMock()
        p4.info = {
            'pid': 3456,
            'name': 'idle',
            'username': 'user2',
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_info': MagicMock(rss=1 * 1024 * 1024),  # 1 MB
            'status': 'sleeping',
            'create_time': 1704070000.0
        }
        processes.append(p4)
        
        return processes
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_returns_correct_structure(self, mock_process_iter, mock_process_list):
        """Test that collect() returns the correct data structure."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Verify data structure
        assert 'processes' in data
        assert 'total_count' in data
        
        # Verify data types
        assert isinstance(data['processes'], list)
        assert isinstance(data['total_count'], int)
        assert data['total_count'] == 4
        
        # Verify process structure
        if data['processes']:
            proc = data['processes'][0]
            assert 'pid' in proc
            assert 'name' in proc
            assert 'user' in proc
            assert 'cpu_percent' in proc
            assert 'memory_percent' in proc
            assert 'memory_mb' in proc
            assert 'status' in proc
            assert 'create_time' in proc
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_sorts_by_cpu_by_default(self, mock_process_iter, mock_process_list):
        """Test that processes are sorted by CPU percentage by default."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        processes = data['processes']
        
        # Verify sorting: highest CPU first
        assert processes[0]['pid'] == 1234  # 75.5% CPU
        assert processes[1]['pid'] == 9012  # 10.0% CPU
        assert processes[2]['pid'] == 5678  # 2.1% CPU
        assert processes[3]['pid'] == 3456  # 0.0% CPU
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_sorts_by_memory(self, mock_process_iter, mock_process_list):
        """Test that processes can be sorted by memory percentage."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect(sort_by='memory_percent', reverse=True)
        
        processes = data['processes']
        
        # Verify sorting: highest memory first
        assert processes[0]['pid'] == 5678  # 15.8% memory
        assert processes[1]['pid'] == 1234  # 5.2% memory
        assert processes[2]['pid'] == 9012  # 0.5% memory
        assert processes[3]['pid'] == 3456  # 0.0% memory
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_sorts_by_pid(self, mock_process_iter, mock_process_list):
        """Test that processes can be sorted by PID."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect(sort_by='pid', reverse=False)
        
        processes = data['processes']
        
        # Verify sorting: lowest PID first
        assert processes[0]['pid'] == 1234
        assert processes[1]['pid'] == 3456
        assert processes[2]['pid'] == 5678
        assert processes[3]['pid'] == 9012
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_sorts_by_name(self, mock_process_iter, mock_process_list):
        """Test that processes can be sorted by name."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect(sort_by='name', reverse=False)
        
        processes = data['processes']
        
        # Verify sorting: alphabetical order
        assert processes[0]['name'] == 'chrome'
        assert processes[1]['name'] == 'idle'
        assert processes[2]['name'] == 'python'
        assert processes[3]['name'] == 'systemd'
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_handles_nosuchprocess_exception(self, mock_process_iter):
        """Test that NoSuchProcess exceptions are handled gracefully."""
        import psutil
        
        # Create a process that raises NoSuchProcess
        bad_process = MagicMock()
        bad_process.info = {}
        
        # Configure the mock to raise exception when accessing info
        type(bad_process).info = property(
            lambda self: (_ for _ in ()).throw(psutil.NoSuchProcess(1234))
        )
        
        # Mix good and bad processes
        good_process = MagicMock()
        good_process.info = {
            'pid': 1234,
            'name': 'test',
            'username': 'user',
            'cpu_percent': 10.0,
            'memory_percent': 5.0,
            'memory_info': MagicMock(rss=50 * 1024 * 1024),
            'status': 'running',
            'create_time': 1704067200.0
        }
        
        mock_process_iter.return_value = [good_process, bad_process]
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Should only get the good process
        assert data['total_count'] == 1
        assert data['processes'][0]['pid'] == 1234
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_handles_accessdenied_exception(self, mock_process_iter):
        """Test that AccessDenied exceptions are handled gracefully."""
        import psutil
        
        # Create a process that raises AccessDenied
        restricted_process = MagicMock()
        type(restricted_process).info = property(
            lambda self: (_ for _ in ()).throw(psutil.AccessDenied(1234))
        )
        
        # Add a normal process
        normal_process = MagicMock()
        normal_process.info = {
            'pid': 5678,
            'name': 'accessible',
            'username': 'user',
            'cpu_percent': 5.0,
            'memory_percent': 2.0,
            'memory_info': MagicMock(rss=20 * 1024 * 1024),
            'status': 'running',
            'create_time': 1704067200.0
        }
        
        mock_process_iter.return_value = [restricted_process, normal_process]
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Should only get the accessible process
        assert data['total_count'] == 1
        assert data['processes'][0]['pid'] == 5678
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_handles_none_values(self, mock_process_iter):
        """Test that None values in process info are handled."""
        # Process with some None values
        process = MagicMock()
        process.info = {
            'pid': 1234,
            'name': None,  # Missing name
            'username': None,  # Missing username
            'cpu_percent': None,  # Missing CPU
            'memory_percent': None,  # Missing memory
            'memory_info': None,  # Missing memory info
            'status': None,  # Missing status
            'create_time': None  # Missing create time
        }
        
        mock_process_iter.return_value = [process]
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Should handle None values with defaults
        assert data['total_count'] == 1
        proc = data['processes'][0]
        assert proc['name'] == 'N/A'
        assert proc['user'] == 'N/A'
        assert proc['cpu_percent'] == 0.0
        assert proc['memory_percent'] == 0.0
        assert proc['memory_mb'] == 0.0
        assert proc['status'] == 'unknown'
        assert proc['create_time'] == 0.0
    
    @patch('src.monitors.processes.psutil.Process')
    def test_kill_process_success(self, mock_process_class):
        """Test successful process termination."""
        mock_proc = MagicMock()
        mock_process_class.return_value = mock_proc
        
        monitor = ProcessMonitor()
        result = monitor.kill_process(1234)
        
        # Verify kill was called
        assert result is True
        mock_process_class.assert_called_once_with(1234)
        mock_proc.terminate.assert_called_once()
    
    @patch('src.monitors.processes.psutil.Process')
    def test_kill_process_nosuchprocess(self, mock_process_class):
        """Test killing a non-existent process."""
        import psutil
        
        mock_process_class.side_effect = psutil.NoSuchProcess(1234)
        
        monitor = ProcessMonitor()
        result = monitor.kill_process(1234)
        
        # Should return False for non-existent process
        assert result is False
    
    @patch('src.monitors.processes.psutil.Process')
    def test_kill_process_accessdenied(self, mock_process_class):
        """Test killing a process without permission."""
        import psutil
        
        mock_proc = MagicMock()
        mock_proc.terminate.side_effect = psutil.AccessDenied(1234)
        mock_process_class.return_value = mock_proc
        
        monitor = ProcessMonitor()
        result = monitor.kill_process(1234)
        
        # Should return False when permission denied
        assert result is False
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_with_invalid_sort_field(self, mock_process_iter, mock_process_list):
        """Test that invalid sort fields fall back to default."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        data = monitor.collect(sort_by='invalid_field', reverse=True)
        
        # Should fall back to cpu_percent sorting
        processes = data['processes']
        assert processes[0]['pid'] == 1234  # Highest CPU
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_reverse_sorting(self, mock_process_iter, mock_process_list):
        """Test reverse sorting order."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        
        # Test ascending order
        data = monitor.collect(sort_by='cpu_percent', reverse=False)
        processes = data['processes']
        
        # Verify sorting: lowest CPU first
        assert processes[0]['pid'] == 3456  # 0.0% CPU
        assert processes[-1]['pid'] == 1234  # 75.5% CPU
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_monitor_has_no_history(self, mock_process_iter, mock_process_list):
        """Test that ProcessMonitor doesn't maintain history."""
        mock_process_iter.return_value = mock_process_list
        
        monitor = ProcessMonitor()
        
        # Verify history size is 1 (minimal)
        assert monitor.history.maxsize == 1
        
        # Collect data multiple times
        monitor.collect()
        monitor.collect()
        
        # History should still be minimal
        assert len(monitor.history) <= 1
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_memory_mb_calculation(self, mock_process_iter):
        """Test that memory MB is calculated correctly."""
        # Create process with known memory
        process = MagicMock()
        rss_bytes = 100 * 1024 * 1024  # 100 MB
        process.info = {
            'pid': 1234,
            'name': 'test',
            'username': 'user',
            'cpu_percent': 10.0,
            'memory_percent': 5.0,
            'memory_info': MagicMock(rss=rss_bytes),
            'status': 'running',
            'create_time': 1704067200.0
        }
        
        mock_process_iter.return_value = [process]
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Verify memory calculation
        expected_mb = rss_bytes / 1024 / 1024
        assert data['processes'][0]['memory_mb'] == pytest.approx(expected_mb, rel=0.01)
    
    @patch('src.monitors.processes.psutil.process_iter')
    def test_collect_empty_process_list(self, mock_process_iter):
        """Test handling of empty process list."""
        mock_process_iter.return_value = []
        
        monitor = ProcessMonitor()
        data = monitor.collect()
        
        # Should return empty list
        assert data['processes'] == []
        assert data['total_count'] == 0
