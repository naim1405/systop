"""Unit tests for NetworkMonitor class.

Tests network data collection, bandwidth rate calculation, history tracking,
and data structure validation using mocked psutil calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.monitors.network import NetworkMonitor


class TestNetworkMonitor:
    """Test suite for NetworkMonitor class."""
    
    @pytest.fixture
    def mock_net_io_counters(self):
        """Mock network I/O counters."""
        def create_counters(bytes_sent, bytes_recv, packets_sent, packets_recv):
            counters = MagicMock()
            counters.bytes_sent = bytes_sent
            counters.bytes_recv = bytes_recv
            counters.packets_sent = packets_sent
            counters.packets_recv = packets_recv
            return counters
        return create_counters
    
    @patch('src.monitors.network.psutil.net_io_counters')
    def test_collect_returns_correct_structure(
        self,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that collect() returns the correct data structure."""
        # Setup mock
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 5_000_000, 10000, 50000
        )
        
        # Create monitor and collect data
        monitor = NetworkMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify data structure
        assert 'bytes_sent_per_sec' in data
        assert 'bytes_recv_per_sec' in data
        assert 'total_sent' in data
        assert 'total_recv' in data
        assert 'packets_sent' in data
        assert 'packets_recv' in data
        
        # Verify types
        assert isinstance(data['bytes_sent_per_sec'], float)
        assert isinstance(data['bytes_recv_per_sec'], float)
        assert isinstance(data['total_sent'], int)
        assert isinstance(data['total_recv'], int)
        assert isinstance(data['packets_sent'], int)
        assert isinstance(data['packets_recv'], int)
        
        # First call should have zero rates
        assert data['bytes_sent_per_sec'] == 0.0
        assert data['bytes_recv_per_sec'] == 0.0
        
        # But cumulative values should be present
        assert data['total_sent'] == 1_000_000
        assert data['total_recv'] == 5_000_000
        assert data['packets_sent'] == 10000
        assert data['packets_recv'] == 50000
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_rate_calculation(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that bandwidth rates are calculated correctly on second call."""
        # First call network counters
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 5_000_000, 10000, 50000
        )
        mock_time.return_value = 1000.0
        
        # Create monitor and collect first data
        monitor = NetworkMonitor(history_size=60)
        data1 = monitor.collect()
        
        # Verify first call has zero rates
        assert data1['bytes_sent_per_sec'] == 0.0
        assert data1['bytes_recv_per_sec'] == 0.0
        
        # Second call network counters (1 second later)
        # Sent: 1_000_000 -> 1_524_288 (512 KB increase)
        # Recv: 5_000_000 -> 6_048_576 (1 MB increase)
        mock_net_io_func.return_value = mock_net_io_counters(
            1_524_288, 6_048_576, 10100, 50500
        )
        mock_time.return_value = 1001.0
        
        # Collect second data
        data2 = monitor.collect()
        
        # Verify rates are calculated correctly
        # Upload rate: (1_524_288 - 1_000_000) / 1.0 = 524_288 B/s
        # Download rate: (6_048_576 - 5_000_000) / 1.0 = 1_048_576 B/s
        assert data2['bytes_sent_per_sec'] == pytest.approx(524_288.0)
        assert data2['bytes_recv_per_sec'] == pytest.approx(1_048_576.0)
        
        # Verify cumulative values are updated
        assert data2['total_sent'] == 1_524_288
        assert data2['total_recv'] == 6_048_576
        assert data2['packets_sent'] == 10100
        assert data2['packets_recv'] == 50500
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_rate_calculation_with_different_time_delta(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test bandwidth rate calculation with non-1-second intervals."""
        # First call
        mock_net_io_func.return_value = mock_net_io_counters(
            0, 0, 0, 0
        )
        mock_time.return_value = 1000.0
        
        monitor = NetworkMonitor(history_size=60)
        data1 = monitor.collect()
        assert data1['bytes_sent_per_sec'] == 0.0
        
        # Second call (2 seconds later)
        # Sent: 0 -> 2_000_000 (2 MB in 2 seconds = 1 MB/s)
        # Recv: 0 -> 4_000_000 (4 MB in 2 seconds = 2 MB/s)
        mock_net_io_func.return_value = mock_net_io_counters(
            2_000_000, 4_000_000, 2000, 4000
        )
        mock_time.return_value = 1002.0
        
        data2 = monitor.collect()
        
        # Verify rates are per-second averages
        assert data2['bytes_sent_per_sec'] == pytest.approx(1_000_000.0)
        assert data2['bytes_recv_per_sec'] == pytest.approx(2_000_000.0)
    
    @patch('src.monitors.network.psutil.net_io_counters')
    def test_history_tracking(
        self,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that total bandwidth rate is stored in history."""
        # Setup mock
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 5_000_000, 10000, 50000
        )
        
        # Create monitor and collect data
        monitor = NetworkMonitor(history_size=60)
        
        # First collection
        monitor.collect()
        history = monitor.get_history()
        assert len(history) == 1
        # First call should have total rate of 0.0
        assert history[0] == 0.0
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_history_stores_combined_bandwidth(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that history stores combined upload + download bandwidth."""
        # First call
        mock_net_io_func.return_value = mock_net_io_counters(
            0, 0, 0, 0
        )
        mock_time.return_value = 1000.0
        
        monitor = NetworkMonitor(history_size=60)
        monitor.collect()
        
        # Second call (1 second later)
        # Upload: 500 KB/s, Download: 1 MB/s
        mock_net_io_func.return_value = mock_net_io_counters(
            512_000, 1_048_576, 1000, 2000
        )
        mock_time.return_value = 1001.0
        
        monitor.collect()
        history = monitor.get_history()
        
        # History should contain sum of upload and download rates
        # 512_000 + 1_048_576 = 1_560_576
        assert len(history) == 2
        assert history[1] == pytest.approx(1_560_576.0)
    
    @patch('src.monitors.network.psutil.net_io_counters')
    def test_no_network_counters_available(
        self,
        mock_net_io_func
    ):
        """Test behavior when network I/O counters are not available."""
        # Mock returns None
        mock_net_io_func.return_value = None
        
        # Create monitor and collect data
        monitor = NetworkMonitor(history_size=60)
        data = monitor.collect()
        
        # Verify all values are zero
        assert data['bytes_sent_per_sec'] == 0.0
        assert data['bytes_recv_per_sec'] == 0.0
        assert data['total_sent'] == 0
        assert data['total_recv'] == 0
        assert data['packets_sent'] == 0
        assert data['packets_recv'] == 0
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_first_call_handling(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that first call is handled gracefully (no previous data)."""
        # Setup mock
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 5_000_000, 10000, 50000
        )
        mock_time.return_value = 1000.0
        
        # Create monitor and collect data
        monitor = NetworkMonitor(history_size=60)
        data = monitor.collect()
        
        # First call should have zero rates but valid cumulative data
        assert data['bytes_sent_per_sec'] == 0.0
        assert data['bytes_recv_per_sec'] == 0.0
        assert data['total_sent'] == 1_000_000
        assert data['total_recv'] == 5_000_000
        
        # Internal state should be set for next call
        assert monitor._last_stats is not None
        assert monitor._last_stats['bytes_sent'] == 1_000_000
        assert monitor._last_stats['bytes_recv'] == 5_000_000
        assert monitor._last_stats['timestamp'] == 1000.0
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_multiple_collect_calls(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test multiple collect() calls to verify rate calculation consistency."""
        # Create monitor
        monitor = NetworkMonitor(history_size=60)
        
        # First call
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 5_000_000, 10000, 50000
        )
        mock_time.return_value = 1000.0
        data1 = monitor.collect()
        assert data1['bytes_sent_per_sec'] == 0.0
        assert data1['bytes_recv_per_sec'] == 0.0
        
        # Second call (1 second later)
        mock_net_io_func.return_value = mock_net_io_counters(
            2_000_000, 7_000_000, 12000, 60000
        )
        mock_time.return_value = 1001.0
        data2 = monitor.collect()
        assert data2['bytes_sent_per_sec'] == pytest.approx(1_000_000.0)
        assert data2['bytes_recv_per_sec'] == pytest.approx(2_000_000.0)
        
        # Third call (1 second later)
        mock_net_io_func.return_value = mock_net_io_counters(
            3_000_000, 9_000_000, 14000, 70000
        )
        mock_time.return_value = 1002.0
        data3 = monitor.collect()
        assert data3['bytes_sent_per_sec'] == pytest.approx(1_000_000.0)
        assert data3['bytes_recv_per_sec'] == pytest.approx(2_000_000.0)
        
        # Verify history has 3 entries
        history = monitor.get_history()
        assert len(history) == 3
        # Entry 0: 0.0 (first call)
        # Entry 1: 3_000_000.0 (1 MB/s upload + 2 MB/s download)
        # Entry 2: 3_000_000.0 (same rates)
        assert history[0] == 0.0
        assert history[1] == pytest.approx(3_000_000.0)
        assert history[2] == pytest.approx(3_000_000.0)
    
    @patch('src.monitors.network.psutil.net_io_counters')
    @patch('src.monitors.network.time.time')
    def test_zero_time_delta_handling(
        self,
        mock_time,
        mock_net_io_func,
        mock_net_io_counters
    ):
        """Test that zero time delta is handled correctly (no division by zero)."""
        # First call
        mock_net_io_func.return_value = mock_net_io_counters(
            0, 0, 0, 0
        )
        mock_time.return_value = 1000.0
        
        monitor = NetworkMonitor(history_size=60)
        monitor.collect()
        
        # Second call with same timestamp (edge case)
        mock_net_io_func.return_value = mock_net_io_counters(
            1_000_000, 2_000_000, 1000, 2000
        )
        mock_time.return_value = 1000.0  # Same time!
        
        data = monitor.collect()
        
        # Should not crash, rates should remain 0.0
        assert data['bytes_sent_per_sec'] == 0.0
        assert data['bytes_recv_per_sec'] == 0.0
