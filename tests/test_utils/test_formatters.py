"""Tests for formatting functions."""

import pytest
from src.utils.formatters import (
    format_bytes,
    format_percentage,
    format_frequency,
    format_speed,
    format_uptime,
    truncate_string
)


class TestFormatBytes:
    """Test format_bytes function."""
    
    def test_zero_bytes(self):
        """Test 0 bytes."""
        assert format_bytes(0) == "0 B"
    
    def test_bytes_only(self):
        """Test values less than 1 KB."""
        assert format_bytes(1) == "1 B"
        assert format_bytes(500) == "500 B"
        assert format_bytes(1023) == "1023 B"
    
    def test_kilobytes(self):
        """Test KB values."""
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1536) == "1.50 KB"
        assert format_bytes(2048) == "2.00 KB"
        assert format_bytes(1024 * 1023) == "1023.00 KB"
    
    def test_megabytes(self):
        """Test MB values."""
        assert format_bytes(1048576) == "1.00 MB"
        assert format_bytes(1048576 * 2) == "2.00 MB"
        assert format_bytes(1572864) == "1.50 MB"
    
    def test_gigabytes(self):
        """Test GB values."""
        assert format_bytes(1073741824) == "1.00 GB"
        assert format_bytes(1073741824 * 2) == "2.00 GB"
        assert format_bytes(1610612736) == "1.50 GB"
    
    def test_terabytes(self):
        """Test TB values."""
        assert format_bytes(1099511627776) == "1.00 TB"
        assert format_bytes(1099511627776 * 2) == "2.00 TB"
    
    def test_petabytes(self):
        """Test PB values."""
        assert format_bytes(1125899906842624) == "1.00 PB"
        assert format_bytes(1125899906842624 * 2) == "2.00 PB"
    
    def test_custom_precision(self):
        """Test custom precision."""
        assert format_bytes(1536, precision=0) == "2 KB"
        assert format_bytes(1536, precision=1) == "1.5 KB"
        assert format_bytes(1536, precision=3) == "1.500 KB"
    
    def test_negative_bytes(self):
        """Test negative values."""
        assert format_bytes(-1024) == "-1.00 KB"
        assert format_bytes(-1048576) == "-1.00 MB"
    
    def test_none_value(self):
        """Test None value."""
        assert format_bytes(None) == "N/A"
    
    def test_very_large_value(self):
        """Test very large values."""
        huge = 1125899906842624 * 1024  # Beyond PB
        result = format_bytes(huge)
        assert "PB" in result


class TestFormatPercentage:
    """Test format_percentage function."""
    
    def test_zero_percent(self):
        """Test 0%."""
        assert format_percentage(0.0) == "0.0%"
    
    def test_whole_number(self):
        """Test whole number percentage."""
        assert format_percentage(50.0) == "50.0%"
        assert format_percentage(100.0) == "100.0%"
    
    def test_decimal_values(self):
        """Test decimal percentages."""
        assert format_percentage(45.67) == "45.7%"
        assert format_percentage(99.99) == "100.0%"
        assert format_percentage(12.34) == "12.3%"
    
    def test_custom_precision(self):
        """Test custom precision."""
        assert format_percentage(45.678, precision=0) == "46%"
        assert format_percentage(45.678, precision=2) == "45.68%"
        assert format_percentage(45.678, precision=3) == "45.678%"
    
    def test_negative_values(self):
        """Test negative values are clamped to 0."""
        assert format_percentage(-5.0) == "0.0%"
        assert format_percentage(-100.0) == "0.0%"
    
    def test_none_value(self):
        """Test None value."""
        assert format_percentage(None) == "N/A"
    
    def test_over_100(self):
        """Test values over 100%."""
        assert format_percentage(150.0) == "150.0%"
        assert format_percentage(999.9) == "999.9%"


class TestFormatFrequency:
    """Test format_frequency function."""
    
    def test_zero_mhz(self):
        """Test 0 MHz."""
        assert format_frequency(0) == "0.00 GHz"
    
    def test_typical_frequencies(self):
        """Test typical CPU frequencies."""
        assert format_frequency(2400.0) == "2.40 GHz"
        assert format_frequency(3600.0) == "3.60 GHz"
        assert format_frequency(4200.5) == "4.20 GHz"
    
    def test_low_frequencies(self):
        """Test low frequencies."""
        assert format_frequency(800.0) == "0.80 GHz"
        assert format_frequency(1200.0) == "1.20 GHz"
    
    def test_high_frequencies(self):
        """Test high frequencies."""
        assert format_frequency(5000.0) == "5.00 GHz"
        assert format_frequency(6000.0) == "6.00 GHz"
    
    def test_negative_frequency(self):
        """Test negative frequency."""
        assert format_frequency(-2400.0) == "-2.40 GHz"
    
    def test_none_value(self):
        """Test None value."""
        assert format_frequency(None) == "N/A"


class TestFormatSpeed:
    """Test format_speed function."""
    
    def test_zero_speed(self):
        """Test 0 B/s."""
        assert format_speed(0) == "0 B/s"
    
    def test_bytes_per_sec(self):
        """Test B/s values."""
        assert format_speed(100) == "100 B/s"
        assert format_speed(1023) == "1023 B/s"
    
    def test_kilobytes_per_sec(self):
        """Test KB/s values."""
        assert format_speed(1024) == "1.00 KB/s"
        assert format_speed(2048) == "2.00 KB/s"
        assert format_speed(1536) == "1.50 KB/s"
    
    def test_megabytes_per_sec(self):
        """Test MB/s values."""
        assert format_speed(1048576) == "1.00 MB/s"
        assert format_speed(1572864) == "1.50 MB/s"
        assert format_speed(10485760) == "10.00 MB/s"
    
    def test_gigabytes_per_sec(self):
        """Test GB/s values."""
        assert format_speed(1073741824) == "1.00 GB/s"
        assert format_speed(2147483648) == "2.00 GB/s"
    
    def test_terabytes_per_sec(self):
        """Test TB/s values."""
        assert format_speed(1099511627776) == "1.00 TB/s"
    
    def test_negative_speed(self):
        """Test negative speed."""
        assert format_speed(-1024) == "-1.00 KB/s"
        assert format_speed(-1048576) == "-1.00 MB/s"
    
    def test_none_value(self):
        """Test None value."""
        assert format_speed(None) == "N/A"


class TestFormatUptime:
    """Test format_uptime function."""
    
    def test_zero_uptime(self):
        """Test 0 seconds."""
        assert format_uptime(0) == "0s"
    
    def test_seconds_only(self):
        """Test seconds only."""
        assert format_uptime(30) == "30s"
        assert format_uptime(59) == "59s"
    
    def test_minutes_and_seconds(self):
        """Test minutes and seconds."""
        assert format_uptime(60) == "1m 0s"
        assert format_uptime(90) == "1m 30s"
        assert format_uptime(150) == "2m 30s"
    
    def test_hours_minutes_seconds(self):
        """Test hours, minutes, and seconds."""
        assert format_uptime(3600) == "1h 0m 0s"
        assert format_uptime(3665) == "1h 1m 5s"
        assert format_uptime(7384) == "2h 3m 4s"
    
    def test_only_hours(self):
        """Test whole hours."""
        assert format_uptime(7200) == "2h 0m 0s"
        assert format_uptime(10800) == "3h 0m 0s"
    
    def test_large_uptime(self):
        """Test large uptime values."""
        assert format_uptime(86400) == "24h 0m 0s"  # 1 day
        assert format_uptime(172800) == "48h 0m 0s"  # 2 days
    
    def test_negative_uptime(self):
        """Test negative uptime returns N/A."""
        assert format_uptime(-100) == "N/A"
    
    def test_none_value(self):
        """Test None value."""
        assert format_uptime(None) == "N/A"
    
    def test_float_seconds(self):
        """Test float seconds are converted to int."""
        assert format_uptime(90.9) == "1m 30s"
        assert format_uptime(3665.5) == "1h 1m 5s"


class TestTruncateString:
    """Test truncate_string function."""
    
    def test_no_truncation_needed(self):
        """Test strings shorter than max_length."""
        assert truncate_string("short", 10) == "short"
        assert truncate_string("exact", 5) == "exact"
    
    def test_exact_length(self):
        """Test string exactly at max_length."""
        assert truncate_string("exact_length", 12) == "exact_length"
    
    def test_truncation(self):
        """Test truncation with ellipsis."""
        assert truncate_string("very_long_process_name", 15) == "very_long_pr..."
        assert truncate_string("truncate_this_string", 10) == "truncat..."
    
    def test_very_short_max_length(self):
        """Test very short max_length."""
        assert truncate_string("hello", 3) == "..."
        assert truncate_string("hello", 2) == ".."
        assert truncate_string("hello", 1) == "."
    
    def test_empty_string(self):
        """Test empty string."""
        assert truncate_string("", 10) == ""
    
    def test_none_value(self):
        """Test None value."""
        assert truncate_string(None, 10) == "N/A"
    
    def test_unicode_characters(self):
        """Test with unicode characters."""
        assert truncate_string("hello_世界", 8) == "hello_世界"
        assert truncate_string("unicode_🚀_test", 10) == "unicode..."
    
    def test_whitespace(self):
        """Test strings with whitespace."""
        assert truncate_string("hello world", 8) == "hello..."
        assert truncate_string("  spaces  ", 8) == "  spa..."


class TestFormattersEdgeCases:
    """Test edge cases across all formatters."""
    
    def test_all_formatters_with_none(self):
        """Test all formatters handle None."""
        assert format_bytes(None) == "N/A"
        assert format_percentage(None) == "N/A"
        assert format_frequency(None) == "N/A"
        assert format_speed(None) == "N/A"
        assert format_uptime(None) == "N/A"
        assert truncate_string(None, 10) == "N/A"
    
    def test_formatters_with_zero(self):
        """Test formatters with zero values."""
        assert format_bytes(0) == "0 B"
        assert format_percentage(0.0) == "0.0%"
        assert format_frequency(0) == "0.00 GHz"
        assert format_speed(0) == "0 B/s"
        assert format_uptime(0) == "0s"
    
    def test_very_large_numbers(self):
        """Test formatters with very large numbers."""
        huge = 10**18
        assert "PB" in format_bytes(huge) or "TB" in format_bytes(huge)
        assert format_percentage(10000.0) == "10000.0%"
        assert format_frequency(100000.0) == "100.00 GHz"
        assert "TB/s" in format_speed(huge) or "GB/s" in format_speed(huge)
