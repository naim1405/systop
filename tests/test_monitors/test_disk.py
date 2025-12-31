"""Unit tests for DiskMonitor class.

Tests disk data collection, I/O rate calculation, history tracking,
and data structure validation using mocked psutil calls.
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from src.monitors.disk import DiskMonitor


class TestDiskMonitor:
    """Test suite for DiskMonitor class."""
    
    @pytest.fixture
    def mock_partitions(self):
        """Mock disk partition data."""
        partition1 = MagicMock()
        partition1.device = '/dev/sda1'
        partition1.mountpoint = '/'
        partition1.fstype = 'ext4'
        
        partition2 = MagicMock()
        partition2.device = '/dev/sda2'
        partition2.mountpoint = '/home'
        partition2.fstype = 'ext4'
        
        return [partition1, partition2]
    
    @pytest.fixture
    def mock_disk_usage(self):
        """Mock disk usage data for a partition."""
        def create_usage(total, used, free, percent):
            usage = MagicMock()
            usage.total = total
            usage.used = used
            usage.free = free
            usage.percent = percent
            return usage
        return create_usage
    
    @pytest.fixture
    def mock_io_counters(self):
        """Mock disk I/O counters."""
        def create_counters(read_bytes, write_bytes, read_count, write_count):
            counters = MagicMock()
            counters.read_bytes = read_bytes
            counters.write_bytes = write_bytes
            counters.read_count = read_count
            counters.write_count = write_count
            return counters
        return create_counters
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    def test_collect_returns_correct_structure(
        self,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_disk_usage,
        mock_io_counters
    ):
        """Test that collect() returns the correct data structure."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        mock_disk_usage_func.side_effect = [
            mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
            mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0)
        ]
        mock_io_counters_func.return_value = mock_io_counters(
            1_000_000, 500_000, 1000, 500
        )
        
        # Create monitor and collect data
        monitor = DiskMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify data structure
        assert 'partitions' in data
        assert 'io' in data
        
        # Verify partitions
        assert isinstance(data['partitions'], list)
        assert len(data['partitions']) == 2
        
        # Check first partition
        partition1 = data['partitions'][0]
        assert partition1['device'] == '/dev/sda1'
        assert partition1['mountpoint'] == '/'
        assert partition1['fstype'] == 'ext4'
        assert partition1['total'] == 500_000_000_000
        assert partition1['used'] == 250_000_000_000
        assert partition1['free'] == 250_000_000_000
        assert partition1['percent'] == 50.0
        
        # Verify I/O data
        io = data['io']
        assert 'read_bytes_per_sec' in io
        assert 'write_bytes_per_sec' in io
        assert 'read_count' in io
        assert 'write_count' in io
        
        # First call should have zero rates
        assert io['read_bytes_per_sec'] == 0.0
        assert io['write_bytes_per_sec'] == 0.0
        assert io['read_count'] == 1000
        assert io['write_count'] == 500
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    @patch('src.monitors.disk.time.time')
    def test_rate_calculation(
        self,
        mock_time,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_disk_usage,
        mock_io_counters
    ):
        """Test that I/O rates are calculated correctly on second call."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        mock_disk_usage_func.side_effect = [
            mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
            mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0),
            # Second call
            mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
            mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0)
        ]
        
        # First call I/O counters
        mock_io_counters_func.return_value = mock_io_counters(
            1_000_000, 500_000, 1000, 500
        )
        mock_time.return_value = 1000.0
        
        # Create monitor and collect first data
        monitor = DiskMonitor(history_size=60)
        data1 = monitor.collect()
        
        # Verify first call has zero rates
        assert data1['io']['read_bytes_per_sec'] == 0.0
        assert data1['io']['write_bytes_per_sec'] == 0.0
        
        # Second call I/O counters (1 second later)
        # Read: 1_000_000 -> 2_048_576 (1 MB increase)
        # Write: 500_000 -> 1_024_000 (512 KB increase)
        mock_io_counters_func.return_value = mock_io_counters(
            2_048_576, 1_024_000, 1100, 550
        )
        mock_time.return_value = 1001.0
        
        # Collect second data
        data2 = monitor.collect()
        
        # Verify rates are calculated correctly
        # Read rate: (2_048_576 - 1_000_000) / 1.0 = 1_048_576 B/s
        # Write rate: (1_024_000 - 500_000) / 1.0 = 524_000 B/s
        assert data2['io']['read_bytes_per_sec'] == pytest.approx(1_048_576.0)
        assert data2['io']['write_bytes_per_sec'] == pytest.approx(524_000.0)
        assert data2['io']['read_count'] == 1100
        assert data2['io']['write_count'] == 550
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    def test_history_tracking(
        self,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_disk_usage,
        mock_io_counters
    ):
        """Test that total I/O rate is stored in history."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        mock_disk_usage_func.side_effect = [
            mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
            mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0)
        ]
        mock_io_counters_func.return_value = mock_io_counters(
            1_000_000, 500_000, 1000, 500
        )
        
        # Create monitor and collect data
        monitor = DiskMonitor(history_size=60)
        
        # First collection
        monitor.collect()
        history = monitor.get_history()
        assert len(history) == 1
        # First call should have total rate of 0.0
        assert history[0] == 0.0
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    def test_no_io_counters_available(
        self,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_disk_usage
    ):
        """Test behavior when disk I/O counters are not available."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        mock_disk_usage_func.side_effect = [
            mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
            mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0)
        ]
        mock_io_counters_func.return_value = None
        
        # Create monitor and collect data
        monitor = DiskMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify I/O data has zero values
        assert data['io']['read_bytes_per_sec'] == 0.0
        assert data['io']['write_bytes_per_sec'] == 0.0
        assert data['io']['read_count'] == 0
        assert data['io']['write_count'] == 0
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    def test_permission_error_handling(
        self,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_io_counters
    ):
        """Test that partitions with permission errors are skipped."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        # First partition OK, second raises PermissionError
        mock_disk_usage_func.side_effect = [
            MagicMock(total=500_000_000_000, used=250_000_000_000, 
                     free=250_000_000_000, percent=50.0),
            PermissionError("Access denied")
        ]
        mock_io_counters_func.return_value = mock_io_counters(
            1_000_000, 500_000, 1000, 500
        )
        
        # Create monitor and collect data
        monitor = DiskMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify only one partition is returned
        assert len(data['partitions']) == 1
        assert data['partitions'][0]['device'] == '/dev/sda1'
    
    @patch('src.monitors.disk.psutil.disk_partitions')
    @patch('src.monitors.disk.psutil.disk_usage')
    @patch('src.monitors.disk.psutil.disk_io_counters')
    @patch('src.monitors.disk.time.time')
    def test_multiple_collect_calls(
        self,
        mock_time,
        mock_io_counters_func,
        mock_disk_usage_func,
        mock_partitions_func,
        mock_partitions,
        mock_disk_usage,
        mock_io_counters
    ):
        """Test multiple collect() calls to verify rate calculation consistency."""
        # Setup mocks
        mock_partitions_func.return_value = mock_partitions
        
        # Mock disk usage for multiple calls
        usage_calls = []
        for _ in range(6):  # 3 collect calls * 2 partitions
            usage_calls.extend([
                mock_disk_usage(500_000_000_000, 250_000_000_000, 250_000_000_000, 50.0),
                mock_disk_usage(1_000_000_000_000, 600_000_000_000, 400_000_000_000, 60.0)
            ])
        mock_disk_usage_func.side_effect = usage_calls
        
        # Create monitor
        monitor = DiskMonitor(history_size=60)
        
        # First call
        mock_io_counters_func.return_value = mock_io_counters(
            1_000_000, 500_000, 1000, 500
        )
        mock_time.return_value = 1000.0
        data1 = monitor.collect()
        assert data1['io']['read_bytes_per_sec'] == 0.0
        
        # Second call (1 second later)
        mock_io_counters_func.return_value = mock_io_counters(
            2_000_000, 1_000_000, 1100, 600
        )
        mock_time.return_value = 1001.0
        data2 = monitor.collect()
        assert data2['io']['read_bytes_per_sec'] == pytest.approx(1_000_000.0)
        assert data2['io']['write_bytes_per_sec'] == pytest.approx(500_000.0)
        
        # Third call (1 second later)
        mock_io_counters_func.return_value = mock_io_counters(
            3_000_000, 1_500_000, 1200, 700
        )
        mock_time.return_value = 1002.0
        data3 = monitor.collect()
        assert data3['io']['read_bytes_per_sec'] == pytest.approx(1_000_000.0)
        assert data3['io']['write_bytes_per_sec'] == pytest.approx(500_000.0)
        
        # Verify history has 3 entries
        history = monitor.get_history()
        assert len(history) == 3
