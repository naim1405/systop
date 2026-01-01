# Changelog

All notable changes to systop will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-01

### Added - Initial Release

#### Core Features
- Real-time system monitoring TUI application for Linux
- Comprehensive CPU monitoring with per-core usage graphs
- Memory and swap usage tracking with historical graphs
- Disk I/O monitoring and partition usage statistics
- Network bandwidth monitoring for all interfaces
- GPU monitoring support for NVIDIA GPUs (via nvidia-smi)
- System temperature sensor readings
- Interactive process management with full keyboard navigation

#### Monitoring Modules
- `CPUMonitor`: CPU usage, frequency, load averages, and hardware info
- `MemoryMonitor`: RAM and swap usage with detailed statistics
- `DiskMonitor`: Disk I/O rates and partition usage tracking
- `NetworkMonitor`: Network bandwidth and traffic statistics per interface
- `GPUMonitor`: NVIDIA GPU usage, memory, and temperature (with graceful fallback)
- `SensorsMonitor`: System temperature readings (when available)
- `ProcessMonitor`: Process list with sorting, filtering, and management

#### UI Components
- `CPUWidget`: Real-time CPU usage display with per-core graphs using plotext
- `MemoryWidget`: Memory and swap usage with visual bars and history
- `DiskWidget`: Disk I/O speeds and partition usage display
- `NetworkWidget`: Network bandwidth graphs for all interfaces
- `GPUWidget`: GPU metrics display (shows "N/A" when unavailable)
- `SensorsWidget`: Temperature sensor readings (hides when unavailable)
- `ProcessWidget`: Interactive process table with pagination and search

#### Process Management
- Sort processes by CPU usage, memory usage, PID, or name
- Search/filter processes by name with real-time filtering
- Kill processes with confirmation dialog
- Keyboard navigation (up/down, page up/down)
- Page-based navigation for large process lists
- Clear visual feedback for all actions

#### Utilities
- `CircularBuffer`: Thread-safe circular buffer for time-series data
- `formatters`: Human-readable formatting for bytes, percentages, frequencies, and speeds
- `config`: Centralized configuration constants

#### Keybindings
- `q`: Quit application
- `r`: Force refresh all widgets
- `k`: Kill selected process (with confirmation)
- `/`: Enter search mode for processes
- `↑`/`↓`: Navigate process list
- `PgUp`/`PgDn`: Navigate process pages
- `Enter`: Apply search filter
- `Esc`: Clear search and exit search mode

#### Testing
- Comprehensive test suite with pytest
- Unit tests for all monitor modules
- Unit tests for utility functions
- Integration tests for app startup
- Test coverage reporting with pytest-cov
- 95%+ code coverage across core modules

#### Documentation
- Complete README with installation and usage instructions
- Detailed docstrings for all public classes and functions
- Module-level documentation in all packages
- Type hints throughout the codebase
- Build plan and development documentation
- Code examples in docstrings

#### Project Setup
- Python 3.10+ support (tested with Python 3.13)
- Virtual environment configuration
- Requirements specification (requirements.txt)
- Project metadata (pyproject.toml)
- Git repository with proper .gitignore
- Entry point script (main.py)

### Technical Details

#### Dependencies
- `textual>=0.50.0` - Modern TUI framework
- `psutil>=5.9.0` - System and process utilities
- `plotext>=5.2.0` - Terminal-based plotting
- `py-cpuinfo>=9.0.0` - CPU information
- `nvidia-ml-py>=12.560.30` - GPU monitoring
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support

#### Architecture
- Modular design with separation of concerns
- Abstract base class for all monitors
- Widget-based UI with Textual framework
- Thread-safe data collection and storage
- Efficient circular buffers for historical data
- Graceful fallback for unavailable hardware (GPU, sensors)

#### Platform Support
- Linux only (Ubuntu, Debian, Fedora, Arch, etc.)
- Tested on Ubuntu 22.04 LTS and newer
- Requires Python 3.10 or higher
- Terminal with Unicode and color support recommended

### Known Limitations

- GPU monitoring only supports NVIDIA GPUs via nvidia-smi
- Temperature sensors may not be available on virtual machines
- Process termination requires appropriate user permissions
- Platform-specific to Linux (not compatible with Windows/macOS)
- Very long network interface names may be truncated

### Future Roadmap (Not in v0.1.0)

#### Potential Features for Future Releases
- AMD and Intel GPU support
- Configuration file for customization (colors, update intervals)
- Export metrics to file (CSV, JSON)
- Historical data persistence across sessions
- Custom alert thresholds with notifications
- Support for remote system monitoring
- Docker container metrics
- More detailed network statistics (connections, ports)
- Battery information for laptops
- Theme customization

---

## Release Notes

### Version 0.1.0 - Initial Public Release

This is the first public release of systop, a modern system monitoring tool for Linux. The application is feature-complete with comprehensive monitoring capabilities, interactive process management, and a polished terminal user interface.

**Highlights:**
- ✅ All core features implemented and working
- ✅ Comprehensive test coverage (95%+)
- ✅ Complete documentation
- ✅ Stable and ready for daily use

**Tested On:**
- Ubuntu 22.04 LTS
- Python 3.13
- Various terminal emulators (kitty, alacritty, gnome-terminal)

**Installation:**
```bash
git clone <repository-url>
cd task-manager
python3 -m venv env
source env/bin/activate.fish  # or activate for bash
pip install -r requirements.txt
python main.py
```

**Feedback Welcome:**
Please report bugs or request features via GitHub Issues!

---

[0.1.0]: https://github.com/yourusername/systop/releases/tag/v0.1.0
