# systop

A modern, btop-like system monitor TUI (Text User Interface) for Linux, built with Python and Textual.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## Overview

**systop** is a comprehensive system monitoring tool that displays real-time information about your system's resources in a beautiful terminal interface. Inspired by btop, it provides detailed insights into CPU, memory, disk, network, GPU, and process activity with an intuitive and responsive UI.

## Features

### 🖥️ System Monitoring
- **CPU Monitoring**: Real-time CPU usage with per-core graphs and frequency tracking
- **Memory Tracking**: RAM and swap usage with detailed statistics
- **Disk I/O**: Monitor disk read/write speeds and storage usage across all partitions
- **Network Bandwidth**: Real-time upload/download speeds for all network interfaces
- **GPU Monitoring**: NVIDIA GPU usage, memory, and temperature (displays "N/A" if unavailable)
- **Temperature Sensors**: System temperature monitoring (when available)

### 📊 Process Management
- **Interactive Process List**: View all running processes with CPU, memory, and runtime
- **Sorting**: Sort processes by CPU usage, memory, PID, or name
- **Search/Filter**: Quick search functionality to filter processes
- **Pagination**: Navigate through large process lists efficiently
- **Kill Processes**: Terminate processes directly from the interface (with confirmation)

### ⚡ Performance
- **Lightweight**: Minimal CPU and memory overhead
- **Real-time Updates**: Automatic refresh with configurable intervals
- **Efficient Data Collection**: Circular buffers for historical data
- **Responsive UI**: Handles terminal resizing gracefully

## Installation

### Prerequisites
- Linux operating system (tested on Ubuntu 22.04+)
- Python 3.10 or higher
- Terminal with good Unicode support (recommended: kitty, alacritty, or modern gnome-terminal)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd task-manager
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv env
   ```

3. **Activate the virtual environment**:
   
   For bash/zsh:
   ```bash
   source env/bin/activate
   ```
   
   For fish shell:
   ```bash
   source env/bin/activate.fish
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting systop

Run the application with:
```bash
python main.py
```

Or, if installed as a package:
```bash
systop
```

### Keybindings

| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Exit the application |
| `r` | Refresh | Force refresh all widgets |
| `k` | Kill Process | Kill the selected process (requires confirmation) |
| `/` | Search | Enter search mode to filter processes |
| `↑` / `↓` | Navigate | Move up/down in the process list |
| `PgUp` / `PgDn` | Page Navigation | Move between pages in the process list |
| `Enter` | Apply Search | Apply the search filter |
| `Esc` | Clear Search | Exit search mode and clear filter |

### Tips

- **Focus on Process Widget**: Click on the process table or press `Tab` to focus on it for keyboard navigation
- **Search Processes**: Press `/`, type part of a process name, and press `Enter` to filter
- **Kill Process**: Select a process with arrow keys, press `k`, then confirm with `y`
- **View All Data**: Scroll through the widgets to see all system information

## Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python Version**: 3.10 or higher
- **Terminal**: Modern terminal with Unicode and color support

### Python Dependencies
- `textual>=0.50.0` - TUI framework
- `psutil>=5.9.0` - System and process utilities
- `plotext>=5.2.0` - Terminal plotting
- `py-cpuinfo>=9.0.0` - CPU information
- `nvidia-ml-py>=12.560.30` - GPU monitoring (optional, for NVIDIA GPUs)
- `pytest>=7.4.0` - Testing framework (development)
- `pytest-asyncio>=0.21.0` - Async testing support (development)

## Project Structure

```
systop/
├── src/
│   ├── monitors/        # Data collection modules
│   │   ├── cpu.py       # CPU monitoring
│   │   ├── memory.py    # Memory monitoring
│   │   ├── disk.py      # Disk I/O monitoring
│   │   ├── network.py   # Network monitoring
│   │   ├── processes.py # Process management
│   │   ├── gpu.py       # GPU monitoring
│   │   └── sensors.py   # Temperature sensors
│   ├── widgets/         # UI components
│   │   ├── cpu_widget.py
│   │   ├── memory_widget.py
│   │   ├── disk_widget.py
│   │   ├── network_widget.py
│   │   ├── process_widget.py
│   │   ├── gpu_widget.py
│   │   └── sensors_widget.py
│   ├── utils/           # Helper utilities
│   │   ├── formatters.py # Data formatting
│   │   └── history.py    # Historical data tracking
│   ├── app.py           # Main application
│   └── config.py        # Configuration constants
├── tests/               # Test suite
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

## Known Limitations

- **GPU Monitoring**: Only works with NVIDIA GPUs via `nvidia-smi`. AMD and Intel GPUs are not currently supported.
- **Temperature Sensors**: May not be available on virtual machines or systems without sensor support.
- **Process Termination**: Requires appropriate permissions to kill processes. System processes may require root/sudo.
- **Platform**: Linux only. Not compatible with Windows or macOS due to platform-specific system calls.
- **Network Interface Names**: Very long interface names may be truncated in the display.

## Development

### Running Tests

Run the test suite with pytest:
```bash
# Activate virtual environment first
source env/bin/activate.fish

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_monitors/test_cpu.py
```

**Current test status**: 142/142 tests passing, 74% coverage

### Testing Tools

Three test scripts are available:

1. **Automated Test Suite** (< 1 minute):
   ```bash
   pytest tests/ -v
   ```
   Runs all unit and integration tests.

2. **Quick Stability Test** (5 minutes):
   ```bash
   python test_stability.py
   ```
   Monitors memory and CPU usage for 5 minutes to detect leaks and performance issues.

3. **Comprehensive Testing** (45-60 minutes):
   ```bash
   python test_final_verification.py
   ```
   Interactive guide through all manual test cases including:
   - Widget functionality
   - Process widget interactions
   - Keybindings
   - 30-minute performance test
   - Edge cases

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Include docstrings for all public functions and classes
- Keep functions focused and modular

## Contributing

Contributions are welcome! Here's how you can help:

1. **Bug Reports**: Open an issue describing the bug, steps to reproduce, and your environment
2. **Feature Requests**: Open an issue describing the feature and why it would be useful
3. **Pull Requests**: Fork the repo, create a feature branch, and submit a PR

### Contribution Guidelines

- Write tests for new features
- Ensure all tests pass before submitting
- Update documentation as needed
- Follow the existing code style
- Keep commits focused and write clear commit messages

## Troubleshooting

### Common Issues

**GPU shows "N/A"**:
- This is normal if you don't have an NVIDIA GPU
- Ensure `nvidia-smi` is installed and accessible if you do have an NVIDIA GPU

**Temperature sensors not showing**:
- Temperature sensors may not be available on all systems, especially VMs
- Try installing `lm-sensors` package and running `sensors-detect`

**Permission denied when killing processes**:
- You can only kill processes owned by your user
- Use `sudo` to run systop if you need to manage system processes

**High CPU usage**:
- This is normal during initial startup as monitors initialize
- If sustained, try reducing update frequency in `config.py`

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 systop contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- Inspired by [btop](https://github.com/aristocratos/btop)
- Built with [Textual](https://github.com/Textualize/textual)
- Thanks to the Python community for excellent system monitoring libraries

## Contact & Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join the conversation in GitHub Discussions

---

**Enjoy monitoring your system with systop!** 🚀
