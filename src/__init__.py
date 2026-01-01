"""systop - System Monitor TUI Application.

A comprehensive btop-like system monitoring application for Linux that provides
real-time visualization of system resources in a terminal-based user interface.

Features:
    - CPU usage, frequency, and per-core statistics with graphs
    - Memory (RAM/swap) usage with history graphs
    - Disk I/O rates and partition usage
    - Network bandwidth monitoring and traffic statistics
    - GPU metrics (NVIDIA GPUs via pynvml)
    - Temperature sensor readings
    - Interactive process management (sort, search, kill)

Usage:
    Install and run:
        $ pip install -e .
        $ systop
    
    Or run directly:
        $ python -m src.app

Keyboard Shortcuts:
    q: Quit application
    r: Force refresh all widgets
    (Process widget has additional keys for sorting, search, kill)

Requirements:
    - Linux operating system
    - Python 3.10+
    - psutil, textual, plotext, py-cpuinfo
    - Optional: pynvml for GPU monitoring

Author: systop development team
License: MIT
"""

__version__ = "0.1.0"
