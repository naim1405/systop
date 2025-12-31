# Agent Prompts for Building systop

This file contains step-by-step prompts for building the systop application incrementally. Each prompt should be given to an AI agent in a **fresh context window**. Each prompt is self-contained with all necessary context.

---

## Prompt 1: Project Setup and Dependencies

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish
- Git: Already initialized with .gitignore for env/

CURRENT STATUS:
This is Step 1 - Starting fresh. Only the virtual environment and git are set up.

TASK:
Set up project dependencies and configuration files.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 1 for detailed specifications
2. Verify the virtual environment exists at ./env
3. Check current directory structure

YOUR TASKS:
1. Create requirements.txt with all required dependencies:
   - textual>=0.50.0
   - psutil>=5.9.0
   - plotext>=5.2.0
   - py-cpuinfo>=9.0.0
   - GPUtil>=1.4.0
   - pytest>=7.4.0
   - pytest-asyncio>=0.21.0

2. Create pyproject.toml with project metadata (see BUILD_PLAN.md for structure)

3. Install all dependencies:
   - Activate virtual environment
   - Run pip install -r requirements.txt
   - Verify installations

4. Update .gitignore to include Python-specific entries:
   - __pycache__/, *.pyc, *.pyo, *.pyd
   - .pytest_cache/, .coverage, htmlcov/
   - dist/, build/, *.egg-info/
   - .vscode/, .idea/

DELIVERABLES:
- [ ] requirements.txt created with correct versions
- [ ] pyproject.toml created with project metadata
- [ ] All dependencies installed successfully
- [ ] .gitignore updated with Python entries
- [ ] Can run: pip list | grep textual (should show textual installed)

Confirm all dependencies are installed and ready before completing.
```

---

## Prompt 2: Build Utility Modules

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed (textual, psutil, plotext, etc.)
- ✅ pyproject.toml and requirements.txt created
- ✅ .gitignore configured

CURRENT STATUS:
Step 2 - Building foundation utility modules that will be used throughout the app.

TASK:
Create utility modules for data storage and formatting.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 2 for complete specifications and interfaces
2. Verify dependencies are installed: pip list
3. Create src/, src/utils/, and tests/ directory structure

YOUR TASKS:
1. Create src/utils/__init__.py (can be empty)

2. Create src/utils/history.py:
   - Implement CircularBuffer class with thread-safe operations
   - Use collections.deque with maxlen
   - Methods: __init__(maxsize), append(value), get_all(), get_last_n(n), clear()
   - Add proper docstrings
   - See BUILD_PLAN.md for exact interface

3. Create src/utils/formatters.py:
   - Implement all formatting functions:
     - format_bytes(bytes, precision) -> human-readable size
     - format_percentage(value, precision) -> "X.X%"
     - format_frequency(mhz) -> "X.XX GHz"
     - format_speed(bytes_per_sec) -> "X.XX MB/s"
     - format_uptime(seconds) -> "Xh Xm Xs"
     - truncate_string(text, max_length) -> "text..."
   - Handle edge cases (zero, negative, None, very large numbers)
   - Add docstrings with examples

4. Create tests/test_utils/__init__.py

5. Create tests/test_utils/test_history.py:
   - Test buffer initialization
   - Test append and retrieval
   - Test overflow behavior
   - Test thread safety (optional but recommended)
   - Test edge cases

6. Create tests/test_utils/test_formatters.py:
   - Test each formatter function
   - Test edge cases: 0, negative, None, very large values
   - Test precision handling

7. Run tests: pytest tests/test_utils/ -v

DELIVERABLES:
- [ ] src/utils/history.py with CircularBuffer class
- [ ] src/utils/formatters.py with all 6 functions
- [ ] tests/test_utils/test_history.py with comprehensive tests
- [ ] tests/test_utils/test_formatters.py with comprehensive tests
- [ ] All tests pass: pytest tests/test_utils/ -v shows green

Reference BUILD_PLAN.md Step 2 for exact function signatures and examples.
```

---

## Prompt 3: Configuration System

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed
- ✅ src/utils/history.py and formatters.py implemented and tested
- ✅ Unit tests passing

CURRENT STATUS:
Step 3 - Creating centralized configuration system.

TASK:
Create configuration module with all application settings.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 3 for exact specifications
2. Verify src/ directory exists
3. Check that utils are working

YOUR TASKS:
1. Create src/__init__.py with version info:
   """systop - System monitor TUI for Linux"""
   __version__ = "0.1.0"

2. Create src/config.py:
   - Import dataclass from dataclasses
   - Define Config dataclass with ALL settings:
     - UPDATE_INTERVAL_CPU: float = 1.0
     - UPDATE_INTERVAL_MEMORY: float = 1.0
     - UPDATE_INTERVAL_DISK: float = 5.0
     - UPDATE_INTERVAL_NETWORK: float = 1.0
     - UPDATE_INTERVAL_PROCESSES: float = 2.0
     - UPDATE_INTERVAL_GPU: float = 2.0
     - UPDATE_INTERVAL_SENSORS: float = 5.0
     - HISTORY_SIZE: int = 60
     - PROCESS_PAGE_SIZE: int = 20
     - PROCESS_SORT_BY: str = "cpu_percent"
     - SHOW_GPU: bool = True
     - SHOW_SENSORS: bool = True
     - THEME: str = "dark"
   - Add docstrings explaining each setting
   - Create global config instance: config = Config()

3. Structure code for future extensibility (comments noting where config file loading would go)

DELIVERABLES:
- [ ] src/__init__.py created with version
- [ ] src/config.py created with Config dataclass
- [ ] All required settings present with correct defaults
- [ ] Global config instance available
- [ ] Can import: from src.config import config

Reference BUILD_PLAN.md Step 3 for exact field names and values.
```

---

## Prompt 4: Base Monitor Class

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed
- ✅ src/utils/ modules implemented and tested
- ✅ src/config.py created
- ✅ CircularBuffer available for use

CURRENT STATUS:
Step 4 - Creating the abstract base class that all monitors will inherit from.

TASK:
Create BaseMonitor abstract class as foundation for all monitoring modules.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 4 for exact interface specifications
2. Verify CircularBuffer works: from src.utils.history import CircularBuffer
3. Create src/monitors/ directory

YOUR TASKS:
1. Create src/monitors/__init__.py (can be empty or export BaseMonitor)

2. Create src/monitors/base.py:
   - Import ABC, abstractmethod from abc
   - Import CircularBuffer from src.utils.history
   - Import typing (Dict, Any)
   - Implement BaseMonitor abstract class:
     - __init__(self, history_size: int = 60)
       - Initialize self.history = CircularBuffer(maxsize=history_size)
       - Initialize self._last_data = None
     - @abstractmethod collect(self) -> Dict[str, Any]
       - Docstring explaining subclasses must implement this
     - get_history(self) -> list
       - Return self.history.get_all()
     - get_last_data(self) -> Dict[str, Any]
       - Return self._last_data
   - Add comprehensive docstrings

3. Verify the class can be imported:
   - python -c "from src.monitors.base import BaseMonitor; print('OK')"

DELIVERABLES:
- [ ] src/monitors/__init__.py created
- [ ] src/monitors/base.py with BaseMonitor abstract class
- [ ] All required methods present: __init__, collect (abstract), get_history, get_last_data
- [ ] Proper use of ABC and @abstractmethod decorator
- [ ] Can import without errors

This is the foundation for all monitor implementations. See BUILD_PLAN.md Step 4 for exact interface.
```

---

## Prompt 5: Base Application Canvas

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed (textual available)
- ✅ src/utils/ modules working
- ✅ src/config.py created
- ✅ src/monitors/base.py BaseMonitor class exists

CURRENT STATUS:
Step 5 - Building the main Textual application structure with empty containers for widgets.

TASK:
Create the base application canvas with layout structure.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 5 for detailed layout specifications and CSS
2. Review Textual documentation if needed
3. Check existing src/ structure

YOUR TASKS:
1. Create src/app.py:
   - Import from textual.app import App, ComposeResult
   - Import from textual.containers import Container, VerticalScroll
   - Import from textual.widgets import Header, Footer
   
   - Define SystemMonitorApp class extending App:
     - Add CSS property with layout styling:
       - Container borders, margins, padding
       - Color scheme (dark background)
       - Scrolling behavior
     
     - compose(self) -> ComposeResult:
       - yield Header(show_clock=True)
       - with VerticalScroll():
         - yield Container(id="cpu_container")
         - yield Container(id="memory_container")
         - yield Container(id="disk_container")
         - yield Container(id="network_container")
         - yield Container(id="gpu_container")
         - yield Container(id="sensors_container")
         - yield Container(id="process_container")
       - yield Footer()
     
     - on_mount(self) -> None:
       - Empty for now (will add timers later)
     
     - action_quit(self) -> None:
       - self.exit()
     
     - BINDINGS property with ("q", "quit", "Quit")
   
   - Define main() function:
     - app = SystemMonitorApp()
     - app.run()

2. Create main.py in project root:
   - #!/usr/bin/env python3
   - """Entry point for systop application"""
   - from src.app import main
   - if __name__ == "__main__": main()

3. Make main.py executable: chmod +x main.py

4. Test the base canvas:
   - python main.py
   - Should show app with header (with clock), empty containers, footer
   - Press 'q' to quit
   - Verify no errors

DELIVERABLES:
- [ ] src/app.py created with SystemMonitorApp class
- [ ] All 7 widget containers defined (cpu, memory, disk, network, gpu, sensors, process)
- [ ] Header with clock and Footer present
- [ ] CSS styling applied
- [ ] Quit keybinding works ('q')
- [ ] main.py entry point created
- [ ] App runs without errors: python main.py
- [ ] Can quit cleanly with 'q'

See BUILD_PLAN.md Step 5 for exact layout structure and CSS requirements.
```

---

## Prompt 6: CPU Monitoring Module

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed (psutil, cpuinfo, plotext)
- ✅ Utils (formatters, history) working
- ✅ Config system created
- ✅ BaseMonitor class exists
- ✅ Base app canvas working (can run main.py)

CURRENT STATUS:
Step 6 - First complete monitoring module: CPU monitor + widget + integration.

TASK:
Implement full CPU monitoring feature with data collection, display, and integration.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 6 for complete specifications
2. Test that base app runs: python main.py
3. Review BaseMonitor interface
4. Create tests/test_monitors/ directory

YOUR TASKS:

1. Create src/monitors/cpu.py:
   - Import psutil, cpuinfo, typing, BaseMonitor
   - CPUMonitor class extending BaseMonitor
   - __init__ with history_size parameter, call super().__init__()
   - Store CPU info: self._cpu_info = cpuinfo.get_cpu_info()
   - collect() method returns dict with:
     - 'overall_percent': float (psutil.cpu_percent())
     - 'per_core_percent': list of floats (psutil.cpu_percent(percpu=True))
     - 'frequency': dict with current, min, max (psutil.cpu_freq())
     - 'load_avg': dict with 1min, 5min, 15min (os.getloadavg())
     - 'cpu_count': dict with physical, logical (psutil.cpu_count())
     - 'model': str (from cpuinfo)
   - Store overall_percent in self.history
   - Set self._last_data = data before returning

2. Create src/widgets/__init__.py

3. Create src/widgets/cpu_widget.py:
   - Import Widget, reactive, RenderableType, Panel, Table, plotext
   - Import CPUMonitor, format_percentage, format_frequency
   - CPUWidget class extending Widget
   - data = reactive(None)
   - __init__(self, monitor: CPUMonitor)
   - on_mount: self.set_interval(1.0, self.refresh_data)
   - refresh_data: self.data = self.monitor.collect()
   - render() -> RenderableType:
     - If no data: return Panel("Loading CPU data...")
     - Create ASCII graph using plotext (history data, 60 seconds)
     - Create table with:
       - CPU model
       - Overall usage percentage
       - Per-core percentages (formatted)
       - Current frequency
       - Load averages
     - Return Panel with title "CPU"

4. Integrate in src/app.py:
   - Import CPUMonitor and CPUWidget
   - Add __init__ method: self.cpu_monitor = CPUMonitor()
   - In compose(), replace cpu_container line with:
     - yield CPUWidget(self.cpu_monitor).with_id("cpu_container")
   - OR mount widget to existing container in on_mount

5. Create tests/test_monitors/__init__.py

6. Create tests/test_monitors/test_cpu.py:
   - Mock psutil.cpu_percent, cpu_freq, cpu_count, os.getloadavg
   - Mock cpuinfo.get_cpu_info
   - Test CPUMonitor.collect() returns correct structure
   - Test history is populated
   - Test with different CPU configurations
   - Run: pytest tests/test_monitors/test_cpu.py -v

7. Manual testing:
   - python main.py
   - Verify CPU widget displays
   - Check updates every second
   - Verify graph renders
   - Check per-core percentages
   - Press 'q' to quit

DELIVERABLES:
- [ ] src/monitors/cpu.py implemented with CPUMonitor class
- [ ] src/widgets/cpu_widget.py implemented with CPUWidget class
- [ ] Integration in src/app.py complete
- [ ] tests/test_monitors/test_cpu.py with passing tests
- [ ] Manual test successful: python main.py shows working CPU widget with live updates
- [ ] Graph displays correctly
- [ ] No errors or crashes

See BUILD_PLAN.md Step 6 for exact data structures and display requirements.
```

---

## Prompt 7: Memory Monitoring Module

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ Dependencies installed
- ✅ Utils and config working
- ✅ BaseMonitor class exists
- ✅ Base app with CPU widget working
- ✅ CPU monitor and widget fully implemented

CURRENT STATUS:
Step 7 - Adding memory and swap monitoring.

TASK:
Implement memory monitoring module following same pattern as CPU module.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 7 for specifications
2. Review CPU module implementation as reference
3. Verify app is working with CPU widget

YOUR TASKS:

1. Create src/monitors/memory.py:
   - MemoryMonitor class extending BaseMonitor
   - collect() method returns dict with:
     - 'ram': dict with total, available, used, free, percent
     - 'swap': dict with total, used, free, percent
   - Use psutil.virtual_memory() and psutil.swap_memory()
   - Store ram percent and swap percent in history (or separate histories)
   - Set self._last_data before returning

2. Create src/widgets/memory_widget.py:
   - MemoryWidget class extending Widget
   - Similar structure to CPUWidget
   - data = reactive(None)
   - on_mount: set_interval(1.0, self.refresh_data)
   - render() displays:
     - RAM: used/total (formatted bytes), percentage, bar/graph
     - Swap: used/total (formatted bytes), percentage, bar/graph
     - Historical graphs using plotext
   - Use format_bytes from utils.formatters

3. Integration in src/app.py:
   - Import MemoryMonitor and MemoryWidget
   - Add self.memory_monitor = MemoryMonitor() in __init__
   - Mount MemoryWidget to memory_container

4. Create tests/test_monitors/test_memory.py:
   - Mock psutil.virtual_memory and psutil.swap_memory
   - Test collect() returns correct structure
   - Test history population
   - Run: pytest tests/test_monitors/test_memory.py -v

5. Manual testing:
   - python main.py
   - Verify both CPU and Memory widgets display
   - Check memory updates every second
   - Verify RAM and Swap stats are correct

DELIVERABLES:
- [ ] src/monitors/memory.py implemented
- [ ] src/widgets/memory_widget.py implemented
- [ ] Integration in src/app.py complete
- [ ] tests/test_monitors/test_memory.py with passing tests
- [ ] Manual test successful: both CPU and Memory widgets working
- [ ] Memory usage displays correctly with graphs

Reference BUILD_PLAN.md Step 7 for exact data structure.
```

---

## Prompt 8: Disk Monitoring Module

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ CPU and Memory modules working
- ✅ Utils, config, BaseMonitor available
- ✅ App running with CPU and Memory widgets

CURRENT STATUS:
Step 8 - Adding disk usage and I/O monitoring.

TASK:
Implement disk monitoring with partition usage and I/O rate calculation.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 8 for specifications
2. Note: This requires rate calculation (comparing current with previous)
3. Review existing monitor implementations

YOUR TASKS:

1. Create src/monitors/disk.py:
   - DiskMonitor class extending BaseMonitor
   - __init__: Add self._last_io = None for rate calculation
   - collect() method returns dict with:
     - 'partitions': list of dicts (device, mountpoint, fstype, total, used, free, percent)
     - 'io': dict with read_bytes_per_sec, write_bytes_per_sec, read_count, write_count
   - Use psutil.disk_partitions(), psutil.disk_usage(mountpoint), psutil.disk_io_counters()
   - Calculate per-second rates by comparing with self._last_io
   - Store rates in history
   - Handle first call (self._last_io is None)

2. Create src/widgets/disk_widget.py:
   - DiskWidget class extending Widget
   - data = reactive(None)
   - on_mount: set_interval(5.0, self.refresh_data)  # Note: 5 seconds!
   - render() displays:
     - List of partitions with device, mountpoint, used/total, percent
     - Usage bars for each partition
     - Read/write speeds (use format_speed)
     - Graph of I/O rates over time

3. Integration in src/app.py:
   - Import DiskMonitor and DiskWidget
   - Add self.disk_monitor = DiskMonitor() in __init__
   - Mount DiskWidget to disk_container
   - Note: 5-second interval (different from others)

4. Create tests/test_monitors/test_disk.py:
   - Mock psutil disk functions
   - Test rate calculation (call collect() twice)
   - Test with multiple partitions
   - Test first call (no previous data)
   - Run: pytest tests/test_monitors/test_disk.py -v

5. Manual testing:
   - python main.py
   - Verify all partitions listed
   - Check I/O rates update every 5 seconds
   - Generate disk activity (copy files) and verify rates change

DELIVERABLES:
- [ ] src/monitors/disk.py with rate calculation logic
- [ ] src/widgets/disk_widget.py with partition list and I/O graphs
- [ ] Integration in src/app.py (5-second interval)
- [ ] tests/test_monitors/test_disk.py with passing tests
- [ ] Manual test successful: disk widget shows partitions and I/O rates

See BUILD_PLAN.md Step 8 for detailed data structures.
```

---

## Prompt 9: Network Monitoring Module

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ CPU, Memory, and Disk modules working
- ✅ Rate calculation pattern established (see disk module)
- ✅ App running with multiple widgets

CURRENT STATUS:
Step 9 - Adding network bandwidth monitoring.

TASK:
Implement network monitoring with bandwidth rate calculation.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 9 for specifications
2. Review disk module for rate calculation pattern
3. Verify existing widgets working

YOUR TASKS:

1. Create src/monitors/network.py:
   - NetworkMonitor class extending BaseMonitor
   - __init__: Add self._last_stats = None for rate calculation
   - collect() method returns dict with:
     - 'bytes_sent_per_sec': float
     - 'bytes_recv_per_sec': float
     - 'total_sent': int (cumulative)
     - 'total_recv': int (cumulative)
     - 'packets_sent': int
     - 'packets_recv': int
   - Use psutil.net_io_counters()
   - Calculate per-second rates by comparing with self._last_stats
   - Store rates in history (sent and recv separately or combined)
   - Handle first call gracefully

2. Create src/widgets/network_widget.py:
   - NetworkWidget class extending Widget
   - data = reactive(None)
   - on_mount: set_interval(1.0, self.refresh_data)
   - render() displays:
     - Upload speed (use format_speed)
     - Download speed (use format_speed)
     - Total sent/received (use format_bytes)
     - Graphs for upload and download over time using plotext
     - Packet counts (optional)

3. Integration in src/app.py:
   - Import NetworkMonitor and NetworkWidget
   - Add self.network_monitor = NetworkMonitor() in __init__
   - Mount NetworkWidget to network_container
   - 1-second update interval

4. Create tests/test_monitors/test_network.py:
   - Mock psutil.net_io_counters()
   - Test rate calculation
   - Test first call handling
   - Run: pytest tests/test_monitors/test_network.py -v

5. Manual testing:
   - python main.py
   - Generate network traffic (browse web, download file)
   - Verify upload/download speeds update
   - Check graphs display correctly

DELIVERABLES:
- [ ] src/monitors/network.py with rate calculation
- [ ] src/widgets/network_widget.py with bandwidth graphs
- [ ] Integration in src/app.py
- [ ] tests/test_monitors/test_network.py with passing tests
- [ ] Manual test: network widget shows bandwidth with live updates

Reference BUILD_PLAN.md Step 9 for exact data structure.
```

---

## Prompt 10: GPU Monitoring Module (with Fallback)

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ CPU, Memory, Disk, Network modules working
- ✅ GPUtil dependency installed (may not detect GPU)
- ✅ App running with multiple widgets

CURRENT STATUS:
Step 10 - Adding GPU monitoring with graceful fallback for systems without GPU.

TASK:
Implement GPU monitoring that shows "N/A" when GPU unavailable.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 10 for fallback specifications
2. Understand this may show N/A on your system - this is expected!
3. Review existing monitor implementations

YOUR TASKS:

1. Create src/monitors/gpu.py:
   - Import GPUtil with try/except: GPU_AVAILABLE = True/False
   - GPUMonitor class extending BaseMonitor
   - __init__: Check if GPUs actually available with _check_gpus()
   - _check_gpus() method:
     - Try GPUtil.getGPUs()
     - Return True if len(gpus) > 0
     - Return False on any exception
   - collect() -> Optional[List[Dict]]:
     - If not self.available: return None
     - Try to get GPU data
     - Return list of dicts with: id, name, load (0-100), memory_used, memory_total, temperature
     - Return None on any exception
   - Store GPU loads in history (if available)

2. Create src/widgets/gpu_widget.py:
   - GPUWidget class extending Widget
   - data = reactive(None)
   - on_mount: set_interval(2.0, self.refresh_data)  # 2 seconds
   - render() method:
     - If self.data is None: return Panel("GPU: N/A", title="GPU")
     - If data exists: display GPU stats for each GPU:
       - Name, utilization %, memory used/total, temperature
       - Usage bars
   - Handle multiple GPUs if present

3. Integration in src/app.py:
   - Import GPUMonitor and GPUWidget
   - Add self.gpu_monitor = GPUMonitor() in __init__
   - Mount GPUWidget to gpu_container
   - 2-second update interval

4. Create tests/test_monitors/test_gpu.py:
   - Mock GPUtil.getGPUs()
   - Test with GPU available (mock data)
   - Test with GPU unavailable (returns None)
   - Test with import error
   - Run: pytest tests/test_monitors/test_gpu.py -v

5. Manual testing:
   - python main.py
   - If no GPU: should show "GPU: N/A" (this is correct!)
   - If GPU available: should show GPU stats
   - No crashes either way

DELIVERABLES:
- [ ] src/monitors/gpu.py with fallback handling
- [ ] src/widgets/gpu_widget.py showing N/A when unavailable
- [ ] Integration in src/app.py
- [ ] tests/test_monitors/test_gpu.py with passing tests
- [ ] Manual test: GPU shows either N/A or stats, no crashes

IMPORTANT: Showing "GPU: N/A" is EXPECTED and CORRECT behavior on systems without GPU!

See BUILD_PLAN.md Step 10 for exact fallback specifications.
```

---

## Prompt 11: Temperature Sensors Module

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ CPU, Memory, Disk, Network, GPU modules working
- ✅ Fallback pattern established (GPU module)
- ✅ App running smoothly

CURRENT STATUS:
Step 11 - Adding temperature sensor monitoring with conditional display.

TASK:
Implement temperature monitoring that hides section if sensors unavailable.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 11 for specifications
2. This widget may not show on VMs or systems without sensors - expected!
3. Review GPU module for fallback pattern

YOUR TASKS:

1. Create src/monitors/sensors.py:
   - SensorsMonitor class extending BaseMonitor
   - __init__: Check availability with _check_sensors()
   - _check_sensors() method:
     - Try psutil.sensors_temperatures()
     - Return True if temps is not None and len(temps) > 0
     - Return False on AttributeError or if empty
   - collect() -> Optional[Dict]:
     - If not self.available: return None
     - Try psutil.sensors_temperatures()
     - Return sensor dict grouped by type (coretemp, etc.)
     - Each sensor: label, current, high, critical
     - Return None on exception

2. Create src/widgets/sensors_widget.py:
   - SensorsWidget class extending Widget
   - data = reactive(None)
   - on_mount: set_interval(5.0, self.refresh_data)  # 5 seconds
   - render() method:
     - If not self.data or empty: return "" (empty - widget hidden)
     - If data exists: display temperature table
     - Group by sensor type (coretemp, etc.)
     - Show label, current temp, high, critical
     - Format temperatures with units (°C)

3. Integration in src/app.py:
   - Import SensorsMonitor and SensorsWidget
   - Add self.sensors_monitor = SensorsMonitor() in __init__
   - Mount SensorsWidget to sensors_container
   - 5-second update interval
   - Widget will hide itself if no data

4. Create tests/test_monitors/test_sensors.py:
   - Mock psutil.sensors_temperatures()
   - Test with sensors available
   - Test with sensors unavailable (AttributeError)
   - Test with empty sensors dict
   - Run: pytest tests/test_monitors/test_sensors.py -v

5. Manual testing:
   - python main.py
   - If sensors unavailable: section won't show (correct!)
   - If sensors available: temperature table displays
   - No crashes either way

DELIVERABLES:
- [ ] src/monitors/sensors.py with availability check
- [ ] src/widgets/sensors_widget.py that hides when no data
- [ ] Integration in src/app.py
- [ ] tests/test_monitors/test_sensors.py with passing tests
- [ ] Manual test: sensors either show or hide gracefully

IMPORTANT: Not showing sensors is EXPECTED on VMs and some systems!

See BUILD_PLAN.md Step 11 for implementation details.
```

---

## Prompt 12: Process Management Module (Complex)

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ All monitoring modules working (CPU, Memory, Disk, Network, GPU, Sensors)
- ✅ App displays multiple widgets correctly
- ✅ All utilities available (formatters, history, config)

CURRENT STATUS:
Step 12 - Adding complex process management with pagination, search, and kill functionality.
This is the MOST COMPLEX module - take your time!

TASK:
Implement full process management with interactive features.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 12 CAREFULLY - this is detailed and complex
2. Review config.py for PROCESS_PAGE_SIZE and PROCESS_SORT_BY
3. This requires keyboard event handling and state management
4. Plan the implementation before coding

YOUR TASKS:

1. Create src/monitors/processes.py:
   - ProcessMonitor class extending BaseMonitor
   - No history needed: __init__ calls super().__init__(history_size=1)
   - collect(sort_by='cpu_percent', reverse=True) method:
     - Iterate psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time'])
     - Build list of process dicts with: pid, name, user, cpu_percent, memory_percent, memory_mb, status, create_time
     - Handle psutil.NoSuchProcess and psutil.AccessDenied
     - Sort by sort_by field with reverse
     - Return dict with 'processes' list and 'total_count'
   - kill_process(pid: int) -> bool method:
     - Try psutil.Process(pid).terminate()
     - Return True if successful
     - Return False on NoSuchProcess or AccessDenied
     - Handle exceptions gracefully

2. Create src/widgets/process_widget.py (COMPLEX!):
   - ProcessWidget class extending Widget
   - Reactive attributes:
     - current_page = reactive(0)
     - search_term = reactive("")
     - sort_by = reactive("cpu_percent")
     - selected_row = reactive(0)
   - can_focus = True (important!)
   - __init__(monitor: ProcessMonitor):
     - Store monitor reference
     - Load PROCESS_PAGE_SIZE from config
   - on_mount: set_interval(2.0, self.refresh_data)
   - refresh_data method:
     - Call monitor.collect(sort_by=self.sort_by)
     - Filter by search_term if present
     - Calculate pagination
     - Update display
   - render() method:
     - Show search box if active
     - Display process table (PID, Name, User, CPU%, MEM%, Status)
     - Highlight selected row
     - Page indicator: "Page X/Y (Total: Z processes)"
     - Footer with keybindings help
   - Key event handlers:
     - on_key(event) method:
       - 'k': trigger kill_selected_process()
       - '/': activate_search()
       - 'up': move_selection(-1)
       - 'down': move_selection(1)
       - 'pageup': previous_page()
       - 'pagedown': next_page()
       - 'enter' in search: apply search
       - 'escape': clear search
   - kill_selected_process method:
     - Get selected process PID
     - Show confirmation (use app.push_screen or simple flag)
     - If confirmed: call monitor.kill_process(pid)
     - Show result message
   - Pagination logic:
     - Calculate total pages
     - Slice processes for current page
     - Handle page boundaries
   - Search logic:
     - Filter processes by name containing search_term
     - Reset to page 0 on new search

3. Integration in src/app.py:
   - Import ProcessMonitor and ProcessWidget
   - Add self.process_monitor = ProcessMonitor() in __init__
   - Mount ProcessWidget to process_container
   - Ensure widget can receive focus (set can_focus=True)
   - May need to handle focus management

4. Create tests/test_monitors/test_processes.py:
   - Mock psutil.process_iter()
   - Test collect() with different sort orders
   - Test filtering
   - Mock kill_process
   - Test error handling
   - Run: pytest tests/test_monitors/test_processes.py -v

5. Manual testing (THOROUGH!):
   - python main.py
   - Navigate process list with arrow keys
   - Test pagination with PgUp/PgDn
   - Press '/' and search for a process (e.g., "python")
   - Select a process you own (e.g., sleep process)
   - Press 'k' to kill it
   - Confirm kill works (or shows permission error)
   - Test with 1000+ processes
   - Verify no crashes on rapid navigation

DELIVERABLES:
- [ ] src/monitors/processes.py with collect and kill_process
- [ ] src/widgets/process_widget.py with full interactivity
- [ ] Pagination working (20 processes per page)
- [ ] Search functionality working
- [ ] Kill process with confirmation
- [ ] All key handlers working
- [ ] Integration in src/app.py
- [ ] tests/test_monitors/test_processes.py with passing tests
- [ ] Manual testing complete: all features verified

This is the MOST COMPLEX module. Take your time, test thoroughly!
See BUILD_PLAN.md Step 12 for very detailed requirements and patterns.
```

---

## Prompt 13: Polish and Integration

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ All monitoring modules complete (CPU, Memory, Disk, Network, GPU, Sensors, Processes)
- ✅ All widgets working independently
- ✅ App displays all features

CURRENT STATUS:
Step 13 - Polishing and ensuring everything works together seamlessly.

TASK:
Polish the application, fix integration issues, and optimize performance.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 13 for requirements
2. Run the app and identify any rough edges or issues
3. Test all features to find conflicts

YOUR TASKS:

1. Polish src/app.py:
   - Implement graceful shutdown:
     - Add on_unmount() method to cleanup timers
     - Ensure all monitors stop cleanly
   - Add error handling:
     - Wrap widget updates in try/except
     - Display error messages for widget failures
     - Don't let one widget crash the whole app
   - Optimize update scheduling:
     - Consider staggering widget updates to reduce CPU spikes
     - Verify update intervals match config
   - Add loading states:
     - Show "Loading..." during initial data collection
     - Handle empty/null data gracefully
   - Verify all keybindings work correctly

2. Global keybindings:
   - 'q': Quit (should already work)
   - 'r': Force refresh all widgets (add if missing)
   - Tab: Switch focus between widgets (optional but nice)
   - Ensure process widget receives proper focus for its keys

3. Visual polish:
   - Consistent color scheme:
     - Use consistent colors across all widgets
     - Headers, borders, highlights should match
   - Proper spacing and borders:
     - Add margins between widgets
     - Consistent border styles
   - Test responsive layout:
     - Resize terminal to different sizes
     - Ensure widgets adapt gracefully
     - No overlapping or broken layouts
   - Loading indicators:
     - Show spinners or "Loading..." where appropriate
   - User-friendly error messages:
     - "Permission denied" instead of stack traces
     - "No data available" instead of errors

4. Update src/__init__.py:
   - Ensure __version__ = "0.1.0" is present
   - Add proper module docstring

5. Comprehensive manual testing:
   - Test all features together for 5-10 minutes
   - Look for memory leaks (monitor with htop/top)
   - Check for conflicts between widgets
   - Verify CPU usage is reasonable when idle
   - Test rapid interaction (fast scrolling, frequent kills)
   - Verify clean shutdown with 'q'
   - Test edge cases (no processes, no sensors, etc.)

DELIVERABLES:
- [ ] src/app.py with graceful shutdown and error handling
- [ ] All keybindings working ('q', 'r', process keys)
- [ ] Consistent visual styling across widgets
- [ ] Responsive layout tested in different terminal sizes
- [ ] Loading states and error messages implemented
- [ ] src/__init__.py with version info
- [ ] 5-10 minute manual test completed with no issues
- [ ] Memory usage stable (no leaks)
- [ ] CPU usage reasonable

See BUILD_PLAN.md Step 13 for detailed requirements.
```

---

## Prompt 14: Testing Suite

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ All features implemented and working
- ✅ App polished and integrated (Step 13 complete)
- ✅ Some unit tests already exist (from individual modules)

CURRENT STATUS:
Step 14 - Completing comprehensive testing suite.

TASK:
Ensure all code is properly tested with unit and integration tests.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 14 for testing strategy
2. Check which tests already exist in tests/ directory
3. Install pytest and pytest-asyncio if not already done

YOUR TASKS:

1. Review and complete all unit tests:
   - tests/test_monitors/ - Ensure ALL monitors have tests:
     - test_cpu.py
     - test_memory.py
     - test_disk.py
     - test_network.py
     - test_gpu.py
     - test_sensors.py
     - test_processes.py
   - tests/test_utils/ - Ensure all utilities tested:
     - test_formatters.py
     - test_history.py
   - All tests should mock external dependencies (psutil, GPUtil, etc.)
   - Aim for >80% coverage on monitors and utils
   - Each test should:
     - Test happy path
     - Test error conditions
     - Test edge cases

2. Create tests/test_integration.py:
   - Import SystemMonitorApp from src.app
   - Smoke test: test_app_initialization
     - Create app instance
     - Verify it initializes without errors
   - Test: test_app_can_run
     - Use app.run_test() context manager
     - Run for 2-3 seconds
     - Verify no crashes
   - Example:
     ```python
     import pytest
     from src.app import SystemMonitorApp
     
     def test_app_initialization():
         app = SystemMonitorApp()
         assert app is not None
     
     @pytest.mark.asyncio
     async def test_app_runs():
         app = SystemMonitorApp()
         async with app.run_test() as pilot:
             await pilot.pause(2.0)
             # If we get here, app ran successfully
     ```

3. Run full test suite:
   - pytest tests/ -v (verbose output)
   - Check for any failing tests
   - pytest tests/ --cov=src --cov-report=html (optional, generates coverage report)
   - Review coverage report if generated

4. Fix any failing tests:
   - Debug and fix test failures
   - Update mocks if needed
   - Ensure tests are reliable (not flaky)

5. Document untestable features:
   - Create tests/MANUAL_TESTING.md if needed
   - Document UI features that require manual testing
   - Document interactive features (keyboard navigation, etc.)

DELIVERABLES:
- [ ] All monitor tests exist and pass
- [ ] All utility tests exist and pass
- [ ] tests/test_integration.py created with smoke tests
- [ ] Full test suite passes: pytest tests/ -v shows all green
- [ ] Test coverage >80% for monitors and utils
- [ ] Any untestable features documented
- [ ] No flaky tests (run suite 3 times to verify)

Run: pytest tests/ -v --cov=src
Everything should pass!

See BUILD_PLAN.md Step 14 for detailed testing strategy.
```

---

## Prompt 15: Documentation

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ All features implemented and working
- ✅ All tests passing
- ✅ App polished and stable

CURRENT STATUS:
Step 15 - Creating comprehensive documentation for users and contributors.

TASK:
Write complete documentation including README and verify project files.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 15 for README structure
2. Test the app one more time to document accurate behavior
3. Review all keybindings and features

YOUR TASKS:

1. Create comprehensive README.md in project root:
   
   Include these sections:
   - **Project Title and Description**:
     - What is systop
     - What it does (btop-like system monitor)
     - Key features at a glance
   
   - **Features**:
     - Real-time CPU monitoring with per-core graphs
     - Memory and swap usage tracking
     - Disk I/O and usage statistics
     - Network bandwidth monitoring
     - GPU monitoring (NVIDIA, shows N/A if unavailable)
     - Temperature sensors (shows if available)
     - Interactive process management (kill, search, pagination)
   
   - **Installation**:
     ```bash
     git clone <repo>
     cd task-manager
     python -m venv env
     source env/bin/activate.fish  # or activate for bash
     pip install -r requirements.txt
     ```
   
   - **Usage**:
     ```bash
     python main.py
     ```
   
   - **Keybindings Table**:
     | Key | Action |
     |-----|--------|
     | q | Quit application |
     | r | Force refresh all |
     | k | Kill selected process |
     | / | Search processes |
     | ↑/↓ | Navigate process list |
     | PgUp/PgDn | Change page |
     | Esc | Clear search |
   
   - **Requirements**:
     - Linux (tested on Ubuntu 22.04+)
     - Python 3.10 or higher
     - Terminal with good Unicode support
   
   - **Screenshots** (optional but nice):
     - Add ASCII art or describe the layout
   
   - **Known Limitations**:
     - GPU monitoring only works with NVIDIA GPUs
     - Temperature sensors may not be available on VMs
     - Process kill requires appropriate permissions
   
   - **Contributing**:
     - Bug reports welcome
     - Feature requests via issues
     - Code style: follow PEP 8
   
   - **License**:
     - MIT License (or your choice)

2. Verify .gitignore is complete:
   - Check that it includes:
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
     *.swp
     .DS_Store
     ```
   - Add any missing entries

3. Add/verify docstrings:
   - Check all public functions have docstrings
   - Check all classes have docstrings
   - Module-level docstrings in __init__.py files
   - Use proper format:
     ```python
     def function(param: type) -> return_type:
         """Brief description.
         
         Args:
             param: Description
         
         Returns:
             Description of return value
         """
     ```

4. Optional: Create CHANGELOG.md:
   - Document version 0.1.0 features
   - Note initial release

DELIVERABLES:
- [ ] README.md created with all sections
- [ ] Installation instructions clear and tested
- [ ] Usage instructions accurate
- [ ] Keybindings table complete
- [ ] Requirements and limitations documented
- [ ] .gitignore complete and verified
- [ ] All public functions/classes have docstrings
- [ ] Documentation is clear and professional

Test: Clone to a new directory and follow your own README to verify it works!

See BUILD_PLAN.md Step 15 for README structure example.
```

---

## Prompt 16: Final Testing and Verification

```
PROJECT CONTEXT:
- Project: systop - A btop-like system monitor TUI for Linux
- Location: /home/ezio/Documents/personal/task-manager
- Python: 3.13 virtual environment at ./env
- Shell: fish
- Activate env: source env/bin/activate.fish

PREREQUISITES (already complete):
- ✅ All features implemented
- ✅ All tests passing
- ✅ Documentation complete
- ✅ App is polished and stable

CURRENT STATUS:
Step 16 - Final verification and acceptance testing.
This is the FINAL STEP!

TASK:
Perform comprehensive final testing to ensure everything works perfectly.

BEFORE YOU START:
1. Read BUILD_PLAN.md Step 16 for complete checklist
2. Read BUILD_PLAN.md acceptance criteria
3. Prepare to spend 30+ minutes on thorough testing

YOUR TASKS:

1. Complete manual testing checklist:
   
   **Basic Functionality:**
   - [ ] App starts without errors: python main.py
   - [ ] All widgets display (CPU, Memory, Disk, Network, GPU/N/A, Sensors/hidden, Processes)
   - [ ] Data updates in real-time (watch for 30 seconds)
   - [ ] Press 'q' - app quits cleanly
   
   **CPU Widget:**
   - [ ] Overall CPU percentage displays
   - [ ] Per-core percentages show
   - [ ] Graph displays and updates
   - [ ] CPU frequency and load averages visible
   
   **Memory Widget:**
   - [ ] RAM usage displays correctly
   - [ ] Swap usage displays correctly
   - [ ] Graphs update over time
   - [ ] Formatted values (MB/GB) are correct
   
   **Disk Widget:**
   - [ ] All partitions listed
   - [ ] Usage percentages correct
   - [ ] Read/write speeds update
   - [ ] Generate disk activity (cp large file) - speeds reflect it
   
   **Network Widget:**
   - [ ] Upload/download speeds display
   - [ ] Graphs update
   - [ ] Generate network traffic - speeds reflect it
   - [ ] Total transferred amounts shown
   
   **GPU Widget:**
   - [ ] Shows "GPU: N/A" if no GPU (expected)
   - [ ] Shows stats if GPU available
   - [ ] No crashes either way
   
   **Sensors Widget:**
   - [ ] Hidden if no sensors available (expected)
   - [ ] Shows temperatures if available
   - [ ] No crashes either way
   
   **Process Widget (THOROUGH!):**
   - [ ] Process list displays
   - [ ] Press ↓ - selection moves down
   - [ ] Press ↑ - selection moves up
   - [ ] Press PgDn - next page
   - [ ] Press PgUp - previous page
   - [ ] Press '/' - search activates
   - [ ] Type "python" - filters processes
   - [ ] Press Esc - search clears
   - [ ] Select a process you own
   - [ ] Press 'k' - kill confirmation shows
   - [ ] Confirm kill - process terminates (or permission error)
   - [ ] Works with 1000+ processes (check with many tabs/processes)
   
   **Keybindings:**
   - [ ] 'q' quits
   - [ ] 'r' refreshes all
   - [ ] All process widget keys work
   
   **Layout and Responsiveness:**
   - [ ] Resize terminal to 80x24 - still usable
   - [ ] Resize terminal to 200x50 - looks good
   - [ ] No overlapping widgets
   - [ ] Borders and spacing consistent

2. Performance testing (30+ minutes):
   - [ ] Start app: python main.py
   - [ ] Open another terminal: watch 'ps aux | grep python'
   - [ ] Monitor memory usage for 30 minutes
   - [ ] Memory should be stable (not constantly increasing)
   - [ ] CPU usage should be low when system idle (< 5%)
   - [ ] Interact rapidly (scroll fast, search, etc.) - no crashes
   - [ ] Leave app running - should remain stable

3. Edge case testing:
   - [ ] Test with minimal processes (< 20) - pagination correct
   - [ ] Test with many processes (1000+) - performance OK
   - [ ] Kill system process without permission - error message shown
   - [ ] Kill own process - works
   - [ ] Test on different terminal (if available): gnome-terminal, kitty, alacritty
   - [ ] CPU at 100% load (run stress test) - app still responsive

4. Review against acceptance criteria (BUILD_PLAN.md):
   - [ ] All monitoring modules collect and display data correctly
   - [ ] Base canvas renders with all widgets properly placed
   - [ ] Process table supports pagination, search, and kill
   - [ ] GPU and sensors gracefully handle unavailability
   - [ ] Unit tests pass with >80% coverage
   - [ ] Integration smoke test passes
   - [ ] No memory leaks after 30min run
   - [ ] App responds to all keybindings
   - [ ] Code is clean, documented, and follows best practices

5. Document findings:
   - Create a simple summary: "What works, what doesn't"
   - Note any known issues or limitations
   - Verify all issues are documented in README

6. Final verification:
   - [ ] pytest tests/ -v (all tests pass)
   - [ ] python main.py (app starts)
   - [ ] Test for 30+ minutes (stable)
   - [ ] README is accurate
   - [ ] Can hand off to another developer

DELIVERABLES:
- [ ] All manual testing checklist items verified ✓
- [ ] 30+ minute performance test completed
- [ ] No memory leaks detected
- [ ] All edge cases tested
- [ ] Acceptance criteria met
- [ ] Known issues documented
- [ ] Summary of testing results created

FINAL CHECK:
- App is stable, tested, and ready for use
- Documentation is complete and accurate
- All tests pass
- No critical bugs

Congratulations! systop v0.1.0 is complete! 🎉

See BUILD_PLAN.md Step 16 for complete testing checklist.
```

---

## General Instructions for Using These Prompts

**For Each Step:**
1. Copy the prompt exactly as written
2. Give it to the AI agent
3. Ensure the agent reads BUILD_PLAN.md for detailed specs
4. Verify the step is complete before moving to next prompt
5. Test after each step to catch issues early

**Tips:**
- Don't skip steps - they build on each other
- If a step fails, fix it before proceeding
- Run tests after each module is complete
- Manually test the app after each major module (CPU, Memory, etc.)
- The agent should commit to git after each successful step

**Order:**
Follow prompts 1-16 in sequence. Do not proceed to the next prompt until the current one is fully complete and tested.

**Agent Context:**
When giving each prompt to the agent, also provide:
- "The virtual environment is at ./env, activate with: source env/bin/activate.fish"
- "Reference BUILD_PLAN.md for detailed specifications"
- "This is on Linux, using fish shell"
- Any relevant context from previous steps if needed
