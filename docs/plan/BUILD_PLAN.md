# systop - System Monitor TUI Build Plan

## Project Overview
Build a comprehensive btop-like system monitor TUI application for Linux using Python. The application displays real-time CPU, memory, disk, network, GPU, temperature, and process information with interactive features.

**App Name**: `systop`  
**Platform**: Linux only  
**Architecture**: Base canvas with pluggable monitoring modules  
**Tech Stack**: Textual, psutil, plotext, py-cpuinfo, GPUtil

---

## Prerequisites (Already Complete)
- ✅ Python 3.13 virtual environment in `./env`
- ✅ Git repository initialized
- ✅ `.gitignore` configured for `env/`
- Virtual environment activation: `source env/bin/activate.fish`

---

## Project Structure

```
systop/
├── env/                       # Virtual environment (gitignored)
├── src/
│   ├── __init__.py
│   ├── app.py                 # Main Textual application
│   ├── config.py              # Configuration constants
│   ├── monitors/              # Data collection layer
│   │   ├── __init__.py
│   │   ├── base.py           # BaseMonitor abstract class
│   │   ├── cpu.py            # CPU monitoring
│   │   ├── memory.py         # RAM/Swap monitoring
│   │   ├── disk.py           # Disk I/O and usage
│   │   ├── network.py        # Network bandwidth
│   │   ├── processes.py      # Process list
│   │   ├── gpu.py            # GPU monitoring (with fallback)
│   │   └── sensors.py        # Temperature sensors
│   ├── widgets/               # UI components
│   │   ├── __init__.py
│   │   ├── cpu_widget.py
│   │   ├── memory_widget.py
│   │   ├── disk_widget.py
│   │   ├── network_widget.py
│   │   ├── process_widget.py # With pagination and search
│   │   ├── gpu_widget.py
│   │   └── sensors_widget.py
│   └── utils/                 # Helper utilities
│       ├── __init__.py
│       ├── formatters.py     # Format bytes, percentages, etc.
│       └── history.py        # Circular buffer for time-series
├── tests/
│   ├── __init__.py
│   ├── test_monitors/
│   │   ├── __init__.py
│   │   ├── test_cpu.py
│   │   ├── test_memory.py
│   │   ├── test_disk.py
│   │   ├── test_network.py
│   │   └── test_processes.py
│   ├── test_utils/
│   │   ├── __init__.py
│   │   ├── test_formatters.py
│   │   └── test_history.py
│   └── test_integration.py   # Smoke test for app startup
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── pyproject.toml            # Project metadata
├── README.md                  # User documentation
├── BUILD_PLAN.md             # This file
└── .gitignore                # Already exists
```

---

## Step 1: Install Dependencies

### 1.1 Create requirements.txt
```
textual>=0.50.0
psutil>=5.9.0
plotext>=5.2.0
py-cpuinfo>=9.0.0
GPUtil>=1.4.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 1.2 Install packages
```bash
source env/bin/activate.fish
pip install -r requirements.txt
```

### 1.3 Create pyproject.toml
```toml
[project]
name = "systop"
version = "0.1.0"
description = "A btop-like system monitor TUI for Linux"
authors = [{name = "Your Name"}]
requires-python = ">=3.10"
dependencies = [
    "textual>=0.50.0",
    "psutil>=5.9.0",
    "plotext>=5.2.0",
    "py-cpuinfo>=9.0.0",
    "GPUtil>=1.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]

[project.scripts]
systop = "src.app:main"
```

---

## Step 2: Build Utilities (Foundation)

### 2.1 Create src/utils/history.py
**Purpose**: Circular buffer for storing time-series data efficiently

**Requirements**:
- `CircularBuffer` class with fixed size
- Methods: `append(value)`, `get_all()`, `get_last_n(n)`, `clear()`
- Thread-safe operations (use lock)
- Memory efficient (use collections.deque with maxlen)

**Interface**:
```python
class CircularBuffer:
    def __init__(self, maxsize: int = 60):
        """Initialize buffer with max size (default 60 for 1-minute history)"""
        
    def append(self, value: float) -> None:
        """Add new value, automatically removing oldest if full"""
        
    def get_all(self) -> list:
        """Return all values as list"""
        
    def get_last_n(self, n: int) -> list:
        """Return last n values"""
        
    def clear(self) -> None:
        """Clear all values"""
```

### 2.2 Create src/utils/formatters.py
**Purpose**: Format system metrics for display

**Required Functions**:
```python
def format_bytes(bytes: int, precision: int = 2) -> str:
    """Convert bytes to human-readable (B, KB, MB, GB, TB)
    Example: 1536 -> "1.50 KB"
    """

def format_percentage(value: float, precision: int = 1) -> str:
    """Format percentage with % sign
    Example: 45.67 -> "45.7%"
    """

def format_frequency(mhz: float) -> str:
    """Format CPU frequency in GHz
    Example: 2400.0 -> "2.40 GHz"
    """

def format_speed(bytes_per_sec: float) -> str:
    """Format network/disk speed
    Example: 1048576 -> "1.00 MB/s"
    """

def format_uptime(seconds: float) -> str:
    """Format process uptime
    Example: 3665 -> "1h 1m 5s"
    """

def truncate_string(text: str, max_length: int) -> str:
    """Truncate string with ellipsis if too long
    Example: "very_long_process_name" -> "very_long_pr..."
    """
```

### 2.3 Unit Tests for Utils
- Create `tests/test_utils/test_formatters.py`: Test all edge cases (zero, negative, very large numbers, None)
- Create `tests/test_utils/test_history.py`: Test buffer overflow, thread safety, edge cases

---

## Step 3: Create Configuration System

### 3.1 Create src/config.py
**Purpose**: Centralized configuration (hardcoded for now, but extensible)

**Required Settings**:
```python
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    
    # Update intervals (seconds)
    UPDATE_INTERVAL_CPU: float = 1.0
    UPDATE_INTERVAL_MEMORY: float = 1.0
    UPDATE_INTERVAL_DISK: float = 5.0
    UPDATE_INTERVAL_NETWORK: float = 1.0
    UPDATE_INTERVAL_PROCESSES: float = 2.0
    UPDATE_INTERVAL_GPU: float = 2.0
    UPDATE_INTERVAL_SENSORS: float = 5.0
    
    # History settings
    HISTORY_SIZE: int = 60  # Keep 60 data points for graphs
    
    # Process table settings
    PROCESS_PAGE_SIZE: int = 20  # Processes per page
    PROCESS_SORT_BY: str = "cpu_percent"  # Default sort
    
    # Display settings
    SHOW_GPU: bool = True  # Try to show GPU, fallback to N/A
    SHOW_SENSORS: bool = True  # Try to show temps, hide if unavailable
    
    # Theme (for future extension)
    THEME: str = "dark"

# Global config instance
config = Config()
```

---

## Step 4: Build Monitor Base Class

### 4.1 Create src/monitors/base.py
**Purpose**: Abstract base class for all monitors

**Requirements**:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from src.utils.history import CircularBuffer

class BaseMonitor(ABC):
    """Base class for system monitors"""
    
    def __init__(self, history_size: int = 60):
        """Initialize with circular buffer for history"""
        self.history = CircularBuffer(maxsize=history_size)
        self._last_data = None
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Collect current system metrics.
        Must return a dictionary with metric data.
        Should store appropriate metrics in self.history.
        """
        pass
    
    def get_history(self) -> list:
        """Return all historical data points"""
        return self.history.get_all()
    
    def get_last_data(self) -> Dict[str, Any]:
        """Return most recent collected data"""
        return self._last_data
```

---

## Step 5: Build Base Canvas (Main App)

### 5.1 Create src/app.py
**Purpose**: Main Textual application with layout structure

**Requirements**:
- Define overall layout with containers for each widget
- Setup keyboard bindings (q=quit, k=kill process, /=search)
- Initialize update timers (don't start data collection yet)
- Use Textual's Container, VerticalScroll, Header, Footer
- CSS styling for layout (margins, borders, colors)

**Layout Structure**:
```
- Header (app title "systop", current time)
- VerticalScroll container:
  - cpu_container (for CPU widget)
  - memory_container (for Memory widget)
  - disk_container (for Disk widget)
  - network_container (for Network widget)
  - gpu_container (for GPU widget - may show N/A)
  - sensors_container (for Temp sensors - may be empty)
  - process_container (for Process table)
- Footer (keybindings help)
```

**Key Methods**:
```python
class SystemMonitorApp(App):
    CSS = """
    /* Define layout styling */
    """
    
    def compose(self) -> ComposeResult:
        """Build UI structure with empty containers"""
        yield Header()
        with VerticalScroll():
            yield Container(id="cpu_container")
            yield Container(id="memory_container")
            yield Container(id="disk_container")
            yield Container(id="network_container")
            yield Container(id="gpu_container")
            yield Container(id="sensors_container")
            yield Container(id="process_container")
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup after UI is mounted (timers, etc.)"""
        pass
    
    def action_quit(self) -> None:
        """Quit application"""
        self.exit()

def main():
    """Entry point for application"""
    app = SystemMonitorApp()
    app.run()
```

### 5.2 Create main.py
```python
#!/usr/bin/env python3
"""Entry point for systop application"""

from src.app import main

if __name__ == "__main__":
    main()
```

### 5.3 Test Base Canvas
Run the app to ensure layout renders correctly (empty containers):
```bash
python main.py
```
Should show empty app with header, footer, and containers.

---

## Step 6: Develop CPU Module

### 6.1 Create src/monitors/cpu.py
**Purpose**: Collect CPU metrics using psutil

**Data to Collect**:
- Overall CPU percentage
- Per-core CPU percentages
- CPU frequency (current, min, max)
- Load averages (1min, 5min, 15min)
- CPU count (physical, logical)
- CPU model name (using py-cpuinfo)

**Implementation Requirements**:
```python
import psutil
import cpuinfo
from typing import Dict, List, Any
from src.monitors.base import BaseMonitor

class CPUMonitor(BaseMonitor):
    def __init__(self, history_size: int = 60):
        super().__init__(history_size)
        self._cpu_info = cpuinfo.get_cpu_info()
        
    def collect(self) -> Dict[str, Any]:
        """
        Collect CPU metrics
        
        Returns:
        {
            'overall_percent': float,
            'per_core_percent': List[float],
            'frequency': {'current': float, 'min': float, 'max': float},
            'load_avg': {'1min': float, '5min': float, '15min': float},
            'cpu_count': {'physical': int, 'logical': int},
            'model': str
        }
        """
        # Use psutil.cpu_percent(interval=None, percpu=True)
        # Use psutil.cpu_freq()
        # Use os.getloadavg()
        # Store overall_percent in self.history for graphing
```

### 6.2 Create src/widgets/cpu_widget.py
**Purpose**: Display CPU information with graphs

**Display Requirements**:
- Title: "CPU - [Model Name]"
- Overall CPU usage with percentage
- Graph of overall CPU usage over time (using plotext)
- Per-core usage bars or mini-graphs
- CPU frequency display
- Load averages

**Implementation Requirements**:
```python
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
import plotext as plt
from src.monitors.cpu import CPUMonitor

class CPUWidget(Widget):
    data = reactive(None)
    
    def __init__(self, monitor: CPUMonitor):
        super().__init__()
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic updates"""
        self.set_interval(1.0, self.refresh_data)
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor"""
        self.data = self.monitor.collect()
        
    def render(self) -> RenderableType:
        """Render CPU widget with graphs and stats"""
        if not self.data:
            return Panel("Loading CPU data...")
        
        # Create graph using plotext
        # Create table with stats
        # Return Panel with content
```

**Graph Requirements**:
- Use plotext to create ASCII graph
- X-axis: time (last 60 seconds)
- Y-axis: percentage (0-100%)
- Line graph of overall CPU usage

### 6.3 Integrate CPU Widget into App
In `src/app.py`:
- Import CPUMonitor and CPUWidget
- Instantiate monitor in __init__
- Mount widget to cpu_container in compose()

### 6.4 Unit Tests
Create `tests/test_monitors/test_cpu.py`:
- Mock psutil functions
- Test CPUMonitor.collect() returns correct structure
- Test history buffer is populated
- Test error handling (psutil exceptions)

### 6.5 Manual Testing
Run app and verify:
- CPU usage updates every second
- Graph displays correctly
- Per-core percentages shown
- No crashes or errors

---

## Step 7: Develop Memory Module

### 7.1 Create src/monitors/memory.py
**Purpose**: Collect memory and swap metrics

**Data to Collect**:
- RAM: total, available, used, free, percent
- Swap: total, used, free, percent

**Implementation**:
```python
import psutil
from typing import Dict, Any
from src.monitors.base import BaseMonitor

class MemoryMonitor(BaseMonitor):
    def collect(self) -> Dict[str, Any]:
        """
        Returns:
        {
            'ram': {
                'total': int,
                'available': int,
                'used': int,
                'free': int,
                'percent': float
            },
            'swap': {
                'total': int,
                'used': int,
                'free': int,
                'percent': float
            }
        }
        """
        # Use psutil.virtual_memory()
        # Use psutil.swap_memory()
        # Store ram percent and swap percent in history
```

### 7.2 Create src/widgets/memory_widget.py
**Purpose**: Display memory usage with graphs

**Display Requirements**:
- RAM section: used/total, percentage, bar or graph
- Swap section: used/total, percentage, bar or graph
- Historical graph for both RAM and Swap

**Implementation**: Similar to CPUWidget pattern

### 7.3 Integration and Testing
- Integrate into app.py
- Unit tests in `tests/test_monitors/test_memory.py`
- Manual testing

---

## Step 8: Develop Disk Module

### 8.1 Create src/monitors/disk.py
**Purpose**: Collect disk usage and I/O metrics

**Data to Collect**:
- Disk usage per partition (path, total, used, free, percent)
- Disk I/O: read_bytes/sec, write_bytes/sec, read_count, write_count

**Implementation**:
```python
import psutil
from typing import Dict, List, Any
from src.monitors.base import BaseMonitor

class DiskMonitor(BaseMonitor):
    def __init__(self, history_size: int = 60):
        super().__init__(history_size)
        self._last_io = None  # For calculating rates
        
    def collect(self) -> Dict[str, Any]:
        """
        Returns:
        {
            'partitions': [
                {'device': str, 'mountpoint': str, 'fstype': str,
                 'total': int, 'used': int, 'free': int, 'percent': float}
            ],
            'io': {
                'read_bytes_per_sec': float,
                'write_bytes_per_sec': float,
                'read_count': int,
                'write_count': int
            }
        }
        """
        # Use psutil.disk_partitions()
        # Use psutil.disk_usage(mountpoint)
        # Use psutil.disk_io_counters()
        # Calculate rates by comparing with self._last_io
```

### 8.2 Create src/widgets/disk_widget.py
**Display Requirements**:
- List of partitions with usage bars
- I/O rates (read/write speed)
- Graph of I/O over time

### 8.3 Integration and Testing
- Update interval: 5 seconds
- Unit tests
- Manual testing

---

## Step 9: Develop Network Module

### 9.1 Create src/monitors/network.py
**Purpose**: Collect network bandwidth metrics

**Data to Collect**:
- Bytes sent/received per second
- Total bytes sent/received
- Packets sent/received
- Per-interface stats (optional)

**Implementation**:
```python
import psutil
from typing import Dict, Any
from src.monitors.base import BaseMonitor

class NetworkMonitor(BaseMonitor):
    def __init__(self, history_size: int = 60):
        super().__init__(history_size)
        self._last_stats = None
        
    def collect(self) -> Dict[str, Any]:
        """
        Returns:
        {
            'bytes_sent_per_sec': float,
            'bytes_recv_per_sec': float,
            'total_sent': int,
            'total_recv': int,
            'packets_sent': int,
            'packets_recv': int
        }
        """
        # Use psutil.net_io_counters()
        # Calculate rates by comparing with self._last_stats
        # Store rates in history
```

### 9.2 Create src/widgets/network_widget.py
**Display Requirements**:
- Upload speed (formatted with format_speed)
- Download speed (formatted with format_speed)
- Graphs for upload and download over time
- Total transferred

### 9.3 Integration and Testing

---

## Step 10: Develop GPU Module (with Fallback)

### 10.1 Create src/monitors/gpu.py
**Purpose**: Collect GPU metrics with graceful fallback

**Data to Collect**:
- GPU name
- GPU utilization %
- Memory used/total
- Temperature
- If GPUtil fails: return None

**Implementation**:
```python
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from typing import Dict, Any, Optional, List
from src.monitors.base import BaseMonitor

class GPUMonitor(BaseMonitor):
    def __init__(self, history_size: int = 60):
        super().__init__(history_size)
        self.available = GPU_AVAILABLE and self._check_gpus()
        
    def _check_gpus(self) -> bool:
        """Check if GPUs are actually available"""
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
    
    def collect(self) -> Optional[List[Dict[str, Any]]]:
        """
        Returns None if GPU not available, otherwise:
        [
            {
                'id': int,
                'name': str,
                'load': float,  # 0-100
                'memory_used': int,
                'memory_total': int,
                'temperature': float
            }
        ]
        """
        if not self.available:
            return None
        
        try:
            # Use GPUtil.getGPUs()
            # Return list of GPU data
        except Exception:
            return None
```

### 10.2 Create src/widgets/gpu_widget.py
**Display Requirements**:
- If data is None: Display "GPU: N/A" or "No GPU detected"
- If data exists: Show GPU stats with usage bars

**Implementation**:
```python
def render(self) -> RenderableType:
    if self.data is None:
        return Panel("GPU: N/A", title="GPU")
    
    # Render GPU stats
```

### 10.3 Integration and Testing
- Test on system without GPU (should show N/A)
- Test with mocked GPUtil

---

## Step 11: Develop Temperature Sensors Module

### 11.1 Create src/monitors/sensors.py
**Purpose**: Collect temperature sensor data

**Data to Collect**:
- All available temperature sensors
- Sensor label, current temp, high temp, critical temp

**Implementation**:
```python
import psutil
from typing import Dict, List, Any, Optional
from src.monitors.base import BaseMonitor

class SensorsMonitor(BaseMonitor):
    def __init__(self, history_size: int = 60):
        super().__init__(history_size)
        self.available = self._check_sensors()
        
    def _check_sensors(self) -> bool:
        """Check if temperature sensors are available"""
        try:
            temps = psutil.sensors_temperatures()
            return temps is not None and len(temps) > 0
        except AttributeError:
            return False
    
    def collect(self) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        Returns None if sensors not available, otherwise:
        {
            'coretemp': [
                {'label': str, 'current': float, 'high': float, 'critical': float}
            ],
            ...
        }
        """
        if not self.available:
            return None
        
        try:
            return psutil.sensors_temperatures()
        except:
            return None
```

### 11.2 Create src/widgets/sensors_widget.py
**Display Requirements**:
- If data is None or empty: Don't display widget at all (empty container)
- If data exists: Show temperature table grouped by sensor type

**Implementation**:
```python
def render(self) -> RenderableType:
    if not self.data:
        return ""  # Empty - won't show
    
    # Render temperature table
```

### 11.3 Integration and Testing
- Test on system with/without sensors
- Conditional mounting in app.py

---

## Step 12: Develop Process Module (Complex)

### 12.1 Create src/monitors/processes.py
**Purpose**: Collect process information with sorting

**Data to Collect**:
- List of all processes: PID, name, user, CPU%, memory%, status
- Sortable by any field
- Total process count

**Implementation**:
```python
import psutil
from typing import Dict, List, Any
from src.monitors.base import BaseMonitor

class ProcessMonitor(BaseMonitor):
    def __init__(self):
        super().__init__(history_size=1)  # Don't need history
        
    def collect(self, sort_by: str = 'cpu_percent', 
                reverse: bool = True) -> Dict[str, Any]:
        """
        Returns:
        {
            'processes': [
                {
                    'pid': int,
                    'name': str,
                    'user': str,
                    'cpu_percent': float,
                    'memory_percent': float,
                    'memory_mb': float,
                    'status': str,
                    'create_time': float
                }
            ],
            'total_count': int
        }
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 
                                         'cpu_percent', 'memory_percent', 
                                         'memory_info', 'status', 'create_time']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'user': pinfo['username'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'memory_mb': pinfo['memory_info'].rss / 1024 / 1024,
                    'status': pinfo['status'],
                    'create_time': pinfo['create_time']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort processes
        processes.sort(key=lambda x: x[sort_by], reverse=reverse)
        
        return {
            'processes': processes,
            'total_count': len(processes)
        }
    
    def kill_process(self, pid: int) -> bool:
        """Attempt to kill process by PID. Returns success status."""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
```

### 12.2 Create src/widgets/process_widget.py
**Purpose**: Display paginated, searchable process table with kill functionality

**Requirements**:
- Pagination (20 processes per page)
- Search filter (filter by process name)
- Sort by clicking column headers (future) or keybindings
- Kill selected process with 'k' key
- Navigation: arrow keys, page up/down

**State Management**:
```python
class ProcessWidget(Widget):
    current_page = reactive(0)
    search_term = reactive("")
    sort_by = reactive("cpu_percent")
    selected_row = reactive(0)
    
    def __init__(self, monitor: ProcessMonitor):
        super().__init__()
        self.monitor = monitor
        self.can_focus = True
```

**Display Requirements**:
- Table with columns: PID, Name, User, CPU%, MEM%, Status
- Search box at top (activated with '/' key)
- Page indicator: "Page 1/5 (Total: 100 processes)"
- Selected row highlighted
- Footer: "k: kill | /: search | ↑↓: navigate | PgUp/PgDn: page"

**Key Handlers**:
```python
def on_key(self, event: Key) -> None:
    if event.key == "k":
        self.kill_selected_process()
    elif event.key == "/":
        self.activate_search()
    elif event.key == "up":
        self.move_selection(-1)
    elif event.key == "down":
        self.move_selection(1)
    # etc.
```

**Kill Process Flow**:
1. User presses 'k' on selected process
2. Show confirmation dialog: "Kill process [name] (PID: [pid])? (y/n)"
3. If yes: call monitor.kill_process(pid)
4. Show result: "Process killed" or "Failed to kill process (permission denied)"

### 12.3 Integration and Testing
- Unit tests for process collection and sorting
- Test kill_process with mocked psutil
- Manual testing: navigation, search, kill

---

## Step 13: Polish and Integration

### 13.1 App-Level Improvements
In `src/app.py`:
- Ensure all widgets are properly integrated
- Implement graceful shutdown (cleanup timers)
- Add error handling for widget failures
- Optimize update scheduling (stagger updates to avoid CPU spikes)
- Add loading states for initial data collection

### 13.2 Keyboard Bindings
Global keybindings in app:
- `q`: Quit
- `r`: Force refresh all
- `f`: Toggle focus between widgets
- Pass through other keys to focused widget (process table)

### 13.3 Visual Polish
- Consistent color scheme
- Proper spacing and borders
- Responsive layout (test in different terminal sizes)
- Loading indicators
- Error messages for failed operations

### 13.4 Update src/__init__.py
```python
"""systop - System monitor TUI for Linux"""
__version__ = "0.1.0"
```

---

## Step 14: Testing Suite

### 14.1 Unit Tests
All tests in `tests/` directory:
- `test_monitors/test_cpu.py`: Mock psutil, test data collection
- `test_monitors/test_memory.py`: Test memory metrics
- `test_monitors/test_disk.py`: Test disk metrics and rate calculation
- `test_monitors/test_network.py`: Test network rate calculation
- `test_monitors/test_processes.py`: Test process collection, sorting, killing
- `test_utils/test_formatters.py`: Test all formatter functions
- `test_utils/test_history.py`: Test circular buffer

### 14.2 Integration Test
Create `tests/test_integration.py`:
```python
import pytest
from src.app import SystemMonitorApp

def test_app_startup():
    """Smoke test: ensure app can start without crashing"""
    app = SystemMonitorApp()
    # Test that app initializes
    assert app is not None
    # Could test compose() returns expected widgets

@pytest.mark.asyncio
async def test_app_runs():
    """Test app can run for a few seconds"""
    app = SystemMonitorApp()
    async with app.run_test() as pilot:
        await pilot.pause(2.0)  # Run for 2 seconds
        # If we get here, app ran successfully
```

### 14.3 Run Tests
```bash
source env/bin/activate.fish
pytest tests/ -v
```

### 14.4 Test Coverage (Optional)
```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

---

## Step 15: Documentation

### 15.1 Create README.md
Include:
- Project description
- Features list
- Screenshot or demo (ASCII art or actual screenshot)
- Installation instructions
- Usage instructions
- Keybindings reference
- Requirements (Linux only)
- Known limitations
- Contributing guidelines
- License

**Example Structure**:
```markdown
# systop

A btop-like system monitor TUI for Linux, built with Python and Textual.

## Features
- Real-time CPU monitoring with per-core graphs
- Memory and swap usage tracking
- Disk I/O and usage statistics
- Network bandwidth monitoring
- GPU monitoring (NVIDIA)
- Temperature sensors
- Interactive process management (kill, search)

## Installation
[Installation steps]

## Usage
[Usage instructions]

## Keybindings
- `q`: Quit
- `k`: Kill selected process
- `/`: Search processes
- `↑/↓`: Navigate process list
- `PgUp/PgDn`: Page through processes

## Requirements
- Linux (tested on Ubuntu 22.04+)
- Python 3.10+

## License
MIT
```

### 15.2 Update .gitignore
Ensure it includes:
```
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.vscode/
.idea/
```

---

## Step 16: Final Testing and Optimization

### 16.1 Manual Testing Checklist
- [ ] App starts without errors
- [ ] All widgets display data correctly
- [ ] Graphs update in real-time
- [ ] Process table pagination works
- [ ] Process search filters correctly
- [ ] Kill process functionality works
- [ ] GPU shows "N/A" if not available
- [ ] Temperature sensors hide if unavailable
- [ ] App handles terminal resize gracefully
- [ ] Memory usage is reasonable (no leaks)
- [ ] CPU usage is low when idle
- [ ] Quit works cleanly (no hanging processes)

### 16.2 Performance Testing
- Run app for extended period (30+ minutes)
- Monitor memory usage: `ps aux | grep python`
- Check for memory leaks
- Verify circular buffers don't grow unbounded
- Optimize if CPU usage is too high

### 16.3 Edge Cases
- Test with many processes (1000+)
- Test with no disk partitions (unlikely but possible)
- Test with no network interfaces
- Test with permission errors (non-root)
- Test on different terminals (kitty, alacritty, gnome-terminal)

---

## Development Best Practices

### Code Style
- Follow PEP 8
- Use type hints for all functions
- Add docstrings to all classes and public methods
- Keep functions small and focused

### Error Handling
- Wrap psutil calls in try-except
- Gracefully handle missing hardware (GPU, sensors)
- Display user-friendly error messages
- Log errors for debugging (consider using logging module)

### Git Workflow
```bash
# Create feature branches
git checkout -b feature/cpu-monitor
# Commit frequently with clear messages
git commit -m "Add CPU monitoring module with per-core tracking"
# Merge when feature complete and tested
git checkout main
git merge feature/cpu-monitor
```

### Commit Message Convention
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `test:` Adding tests
- `docs:` Documentation updates

---

## Troubleshooting Guide

### Common Issues

**Issue**: GPUtil import fails
- **Solution**: GPU monitoring will show "N/A" - this is expected behavior

**Issue**: psutil.sensors_temperatures() returns None
- **Solution**: Temperature widget will be hidden - this is expected on VMs or systems without sensors

**Issue**: Permission denied when killing process
- **Solution**: Display error message to user, suggest running with sudo if needed

**Issue**: Process table is slow with 1000+ processes
- **Solution**: Increase update interval or implement filtering

**Issue**: Textual rendering issues
- **Solution**: Update textual to latest version, check terminal compatibility

---

## Future Enhancements (Out of Scope for v1.0)

- Config file support (~/.config/systop/config.toml)
- In-app settings menu
- Custom color themes
- Export stats to file
- Historical data persistence
- Process search with regex
- Process tree view
- Container monitoring (Docker)
- Remote system monitoring
- Plugin system for custom monitors
- Mouse support for clicking

---

## Implementation Order Summary

1. ✅ Prerequisites (already done)
2. Install dependencies
3. Build utilities (formatters, history buffer)
4. Create config system
5. Build base monitor class
6. **Build base canvas (app structure)**
7. CPU module (monitor + widget + integration)
8. Memory module
9. Disk module
10. Network module
11. GPU module (with fallback)
12. Sensors module (with fallback)
13. Process module (complex: pagination, search, kill)
14. Polish and integration
15. Testing suite
16. Documentation
17. Final testing

---

## Acceptance Criteria

The project is complete when:
- [ ] All monitoring modules collect and display data correctly
- [ ] Base canvas renders with all widgets properly placed
- [ ] Process table supports pagination, search, and kill
- [ ] GPU and sensors gracefully handle unavailability
- [ ] Unit tests pass with >80% coverage for monitors and utils
- [ ] Integration smoke test passes
- [ ] Manual testing checklist complete
- [ ] README documentation complete
- [ ] No memory leaks after 30min run
- [ ] App responds to all keybindings
- [ ] Code is clean, documented, and follows best practices

---

## Notes for AI Agent

**Important Considerations**:
1. **Module Independence**: Each monitor should be completely independent of other monitors
2. **Widget Self-Contained**: Each widget manages its own data fetching and display logic
3. **Error Resilience**: Never crash the app - always handle exceptions gracefully
4. **Performance**: Keep update logic efficient - avoid blocking the event loop
5. **Testability**: Write code that's easy to mock and test
6. **Extensibility**: Structure code to allow future config file support
7. **User Experience**: Prioritize responsive UI and clear feedback

**Testing Strategy**:
- Test each monitor independently before integrating
- Test widgets in isolation when possible
- Manual testing critical for UI/UX
- Always test on actual Linux system (not just unit tests)

**Common Pitfalls to Avoid**:
- Don't call psutil functions in tight loops
- Don't forget to handle psutil.AccessDenied for protected processes
- Don't let history buffers grow unbounded
- Don't block the Textual event loop with heavy computation
- Don't assume all system features are available (GPU, sensors)

**When in Doubt**:
- Prioritize graceful degradation over failing
- Show "N/A" or hide sections rather than error messages
- Follow Textual best practices and examples
- Keep it simple - don't over-engineer

---

**This plan should be followed sequentially. Each step builds on the previous one. Test thoroughly after each step before proceeding to the next.**
