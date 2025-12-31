"""Formatters for displaying system metrics in human-readable format."""

from typing import Optional


def format_bytes(bytes_value: Optional[int], precision: int = 2) -> str:
    """
    Convert bytes to human-readable size with appropriate unit.
    
    Args:
        bytes_value: Number of bytes (can be None)
        precision: Number of decimal places (default 2)
        
    Returns:
        Formatted string with unit (B, KB, MB, GB, TB, PB)
        
    Examples:
        >>> format_bytes(0)
        '0 B'
        >>> format_bytes(1024)
        '1.00 KB'
        >>> format_bytes(1536)
        '1.50 KB'
        >>> format_bytes(1048576)
        '1.00 MB'
        >>> format_bytes(1073741824)
        '1.00 GB'
        >>> format_bytes(None)
        'N/A'
    """
    if bytes_value is None:
        return "N/A"
    
    if bytes_value < 0:
        return f"-{format_bytes(-bytes_value, precision)}"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    # For bytes, don't show decimal places
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    
    return f"{size:.{precision}f} {units[unit_index]}"


def format_percentage(value: Optional[float], precision: int = 1) -> str:
    """
    Format percentage value with % sign.
    
    Args:
        value: Percentage value (0-100, can be None)
        precision: Number of decimal places (default 1)
        
    Returns:
        Formatted percentage string
        
    Examples:
        >>> format_percentage(45.67)
        '45.7%'
        >>> format_percentage(100.0)
        '100.0%'
        >>> format_percentage(0.0)
        '0.0%'
        >>> format_percentage(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    
    # Clamp negative percentages to 0
    if value < 0:
        value = 0.0
    
    return f"{value:.{precision}f}%"


def format_frequency(mhz: Optional[float]) -> str:
    """
    Format CPU frequency in GHz.
    
    Args:
        mhz: Frequency in MHz (can be None)
        
    Returns:
        Formatted frequency string in GHz
        
    Examples:
        >>> format_frequency(2400.0)
        '2.40 GHz'
        >>> format_frequency(3600.5)
        '3.60 GHz'
        >>> format_frequency(None)
        'N/A'
        >>> format_frequency(0)
        '0.00 GHz'
    """
    if mhz is None:
        return "N/A"
    
    if mhz < 0:
        return f"-{format_frequency(-mhz)}"
    
    ghz = mhz / 1000.0
    return f"{ghz:.2f} GHz"


def format_speed(bytes_per_sec: Optional[float]) -> str:
    """
    Format network/disk speed with appropriate unit.
    
    Args:
        bytes_per_sec: Speed in bytes per second (can be None)
        
    Returns:
        Formatted speed string (B/s, KB/s, MB/s, GB/s)
        
    Examples:
        >>> format_speed(1024)
        '1.00 KB/s'
        >>> format_speed(1048576)
        '1.00 MB/s'
        >>> format_speed(1536000)
        '1.46 MB/s'
        >>> format_speed(None)
        'N/A'
        >>> format_speed(0)
        '0 B/s'
    """
    if bytes_per_sec is None:
        return "N/A"
    
    if bytes_per_sec < 0:
        return f"-{format_speed(-bytes_per_sec)}"
    
    units = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
    unit_index = 0
    speed = float(bytes_per_sec)
    
    while speed >= 1024.0 and unit_index < len(units) - 1:
        speed /= 1024.0
        unit_index += 1
    
    # For B/s, don't show decimal places
    if unit_index == 0:
        return f"{int(speed)} {units[unit_index]}"
    
    return f"{speed:.2f} {units[unit_index]}"


def format_uptime(seconds: Optional[float]) -> str:
    """
    Format process/system uptime in human-readable format.
    
    Args:
        seconds: Uptime in seconds (can be None)
        
    Returns:
        Formatted uptime string (e.g., "1h 5m 30s", "45m 10s", "30s")
        
    Examples:
        >>> format_uptime(30)
        '30s'
        >>> format_uptime(90)
        '1m 30s'
        >>> format_uptime(3665)
        '1h 1m 5s'
        >>> format_uptime(86400)
        '24h 0m 0s'
        >>> format_uptime(None)
        'N/A'
        >>> format_uptime(0)
        '0s'
    """
    if seconds is None:
        return "N/A"
    
    if seconds < 0:
        return "N/A"
    
    seconds = int(seconds)
    
    if seconds == 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:  # Show minutes if we have hours
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    
    return " ".join(parts)


def truncate_string(text: Optional[str], max_length: int) -> str:
    """
    Truncate string with ellipsis if too long.
    
    Args:
        text: String to truncate (can be None)
        max_length: Maximum length including ellipsis
        
    Returns:
        Truncated string with "..." if needed
        
    Examples:
        >>> truncate_string("short", 10)
        'short'
        >>> truncate_string("very_long_process_name", 15)
        'very_long_pr...'
        >>> truncate_string("exact_length", 12)
        'exact_length'
        >>> truncate_string(None, 10)
        'N/A'
        >>> truncate_string("", 10)
        ''
    """
    if text is None:
        return "N/A"
    
    if len(text) <= max_length:
        return text
    
    if max_length <= 3:
        return "..."[:max_length]
    
    return text[:max_length - 3] + "..."
