"""Configuration module for systop application.

This module provides centralized configuration management for all application
settings. Currently uses hardcoded defaults but is structured to support
loading from configuration files in the future.
"""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration settings.
    
    This dataclass holds all configuration parameters for the systop application.
    Default values are provided for all settings, making the application ready
    to run without additional configuration.
    
    Future Enhancement:
        Configuration file loading (e.g., from ~/.config/systop/config.toml)
        can be added by implementing a load_config() function that overrides
        these defaults.
    """
    
    # Update intervals (seconds)
    # These control how frequently each monitor collects new data
    
    UPDATE_INTERVAL_CPU: float = 1.0
    """CPU metrics update interval in seconds. Higher frequency for responsive CPU graphs."""
    
    UPDATE_INTERVAL_MEMORY: float = 1.0
    """Memory and swap update interval in seconds."""
    
    UPDATE_INTERVAL_DISK: float = 5.0
    """Disk I/O and usage update interval in seconds. Less frequent as disk metrics change slowly."""
    
    UPDATE_INTERVAL_NETWORK: float = 1.0
    """Network bandwidth update interval in seconds."""
    
    UPDATE_INTERVAL_PROCESSES: float = 2.0
    """Process list update interval in seconds. Balanced for performance vs. freshness."""
    
    UPDATE_INTERVAL_GPU: float = 2.0
    """GPU metrics update interval in seconds. Requires GPUtil."""
    
    UPDATE_INTERVAL_SENSORS: float = 5.0
    """Temperature sensor update interval in seconds. Sensors update slowly."""
    
    # History settings
    
    HISTORY_SIZE: int = 60
    """Number of data points to keep in history buffers. Default 60 = 1 minute at 1Hz."""
    
    # Process table settings
    
    PROCESS_PAGE_SIZE: int = 20
    """Number of processes to display per page in the process table."""
    
    PROCESS_SORT_BY: str = "cpu_percent"
    """Default sorting column for process table. Options: cpu_percent, memory_percent, pid, name."""
    
    # Display settings
    
    SHOW_GPU: bool = True
    """Attempt to display GPU widget. Falls back to N/A message if GPUtil unavailable."""
    
    SHOW_SENSORS: bool = True
    """Attempt to display temperature sensors. Hides widget if no sensors found."""
    
    # Theme (for future extension)
    
    THEME: str = "dark"
    """UI theme name. Currently only 'dark' is supported. Placeholder for future themes."""


# Global configuration instance
# Import this instance throughout the application: from src.config import config
config = Config()
