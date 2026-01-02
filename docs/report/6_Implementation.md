# Chapter 6: Implementation

## 6.1 Development Environment Setup

The implementation of the systop application was carried out entirely on a Linux environment, reflecting the project's explicit focus on Linux as the primary and only supported platform. Development took place on a 64-bit Linux distribution with a modern kernel (4.x or later), providing full access to the `/proc` and `/sys` pseudo-filesystems that underpin most of the system metrics exposed through psutil and related libraries.

Python served as both the implementation language and the "runtime platform" for the project. A dedicated Python 3.13 virtual environment was created in the project directory (the `env/` folder), isolating all dependencies from the system interpreter. The environment was managed using the standard `venv` module, and activated via the Fish shell using the provided activation script. All Python packages—Textual, psutil, plotext, py-cpuinfo, GPUtil, and pytest—were installed from PyPI using `pip` and recorded in both `requirements.txt` and `pyproject.toml`.

The primary development tools were Visual Studio Code and a terminal running the Fish shell. VS Code provided integrated editing, linting, and test running capabilities, while Fish offered an expressive, user-friendly command-line environment. No external compilers were required beyond those implicitly used by the Python toolchain; the project is pure Python and depends only on binary wheels or source distributions supplied by its libraries. Git was used for version control, enabling incremental commits aligned with the 16-step build plan.

Configuration of the environment was deliberately kept simple and reproducible: cloning the repository, creating the virtual environment, installing the dependencies, and invoking the main entry point or the test suite are sufficient to replicate the development setup on any compatible Linux system.

## 6.2 Coding Standards and Version Control Strategy

From the outset, the project adhered to widely accepted Python coding standards in order to keep the codebase readable, maintainable, and consistent. The following conventions were observed throughout the implementation:

- **Naming and Structure**: Modules and packages use lowercase names with underscores (for example, `history.py`, `formatters.py`), while classes use `CamelCase` (for example, `CircularBuffer`, `CPUMonitor`). Functions, methods, and variables are written in `snake_case`, consistent with PEP 8 recommendations.
- **Docstrings and Type Hints**: All public classes and key functions include descriptive docstrings explaining their purpose, parameters, and return values. Where appropriate, static type hints (using the `typing` module) are employed to make interfaces explicit and to support better tooling and readability.
- **Formatting and Style**: Code formatting follows PEP 8, with clear indentation, consistent use of spaces, and line length guidance. Logical blocks of code are separated with blank lines to emphasize structure, and complex conditionals or loops are refactored into helper functions where necessary to keep cyclomatic complexity reasonable.

The version control strategy used Git as the backbone for tracking changes and managing the project's evolution. Rather than a complex branching model, the project was organized around **incremental, task-focused commits** that mirror the steps defined in the build plan. Each major unit of work—such as implementing the utilities, adding a new monitor, or wiring a widget—was captured in one or more commits with meaningful messages describing the changes.

This approach has two main advantages. First, it provides a clear historical record that directly maps to the conceptual phases of the project. Second, it makes it easy to review, revert, or bisect specific features if regressions are detected. The presence of dedicated test modules further reinforces this strategy: completing a step typically meant both code and tests were committed together, ensuring that the repository remained in a runnable and testable state.

## 6.3 Module-wise Implementation

The implementation of systop is organized into a set of cohesive modules, each responsible for a specific slice of functionality. The sections below describe the core modules, their internal logic, and how they collaborate to deliver the overall behavior of the system.

### 6.3.1 Utility Modules

The utilities form the foundational layer of the application and are implemented under the `src/utils/` package. Two modules are particularly central: `history.py` and `formatters.py`.

The `history.py` module defines the `CircularBuffer` class, a lightweight abstraction around Python's `collections.deque` with a fixed `maxlen`. This buffer is used to retain a bounded window of recent metric values (for example, the last 60 CPU usage samples). The class exposes methods for appending new values, retrieving all stored samples, obtaining only the latest `n` samples, and clearing the buffer. The use of a fixed-length deque ensures that memory usage does not grow unbounded, which is critical for long-running monitoring sessions. Thread-safety is addressed via a simple locking mechanism, allowing multiple producers or concurrent access patterns without corrupting the underlying data structure.

The `formatters.py` module provides a collection of pure functions responsible for converting raw numeric values into human-readable strings suitable for display. Functions such as `format_bytes`, `format_percentage`, `format_frequency`, `format_speed`, `format_uptime`, and `truncate_string` encapsulate common formatting logic. For example, `format_bytes` progressively scales values from bytes to kilobytes, megabytes, gigabytes, or terabytes and attaches the appropriate unit, while `format_uptime` converts a number of seconds into an `h m s` representation. Implementing these functions centrally avoids duplication, enforces consistent formatting across widgets, and simplifies unit testing.

### 6.3.2 Configuration Module

The configuration system lives in `src/config.py` and is built around a `Config` dataclass. This class captures all of the tunable parameters of the application, including update intervals for different subsystems (CPU, memory, disk, network, processes, GPU, sensors), the size of historical buffers, process table pagination, default sort keys, and flags controlling the visibility of optional components such as GPU and sensor monitors.

A single, global `config` instance is created at module import time and imported by other parts of the codebase. This pattern centralizes configuration while keeping access straightforward. Although configuration values are currently hard-coded, the design anticipates future extension to configuration files or command-line arguments without requiring structural changes to the rest of the system.

### 6.3.3 Monitor Base Class and Concrete Monitors

All system data collection responsibilities are encapsulated in the `src/monitors/` package. The core abstraction is defined in `base.py` as the `BaseMonitor` class, which establishes a uniform interface and shared behavior for all concrete monitors.

`BaseMonitor` holds a `CircularBuffer` instance and an internal `_last_data` field. Its abstract `collect()` method defines the contract that all subclass monitors must satisfy: each call should gather a coherent snapshot of relevant system metrics, update any historical buffers, store the snapshot in `_last_data`, and return it to callers. Convenience methods such as `get_history()` and `get_last_data()` provide read-only access to historical and latest data.

Concrete monitors—CPU, memory, disk, network, processes, GPU, and sensors—inherit from this base class and specialize the `collect()` method to their domain.

- The **CPU monitor** uses `psutil.cpu_percent`, `psutil.cpu_freq`, and `os.getloadavg` alongside `py-cpuinfo` to assemble a detailed picture of CPU state, including per-core utilization, overall load, current frequency, load averages, and CPU model information. The overall CPU usage percentage is typically stored in the history buffer for graphing.
- The **memory monitor** leverages `psutil.virtual_memory` and `psutil.swap_memory` to report total, used, free, and available RAM and swap, along with percentage usage. Historical graphs are derived from these values.
- The **disk monitor** calls `psutil.disk_partitions` and `psutil.disk_io_counters` to compute both static partition information (capacity, usage) and dynamic I/O rates (reads and writes per second, throughput). It computes deltas between successive samples to convert cumulative counters into rates.
- The **network monitor** operates similarly, using `psutil.net_io_counters` to track bytes sent and received, packet counts, and to derive bandwidth usage by comparing successive snapshots over the time interval.
- The **process monitor** enumerates active processes with `psutil.process_iter`, collecting attributes such as PID, name, owning user, CPU percentage, memory usage, and status. It organizes the resulting collection into pages, supports sorting by different criteria, and underpins the interactive process management widget.
- The **GPU monitor** (where supported) queries GPUtil or `nvidia-smi`-backed APIs to obtain GPU utilization, memory usage, and temperature. All calls are guarded with exception handling and feature flags so that systems without compatible GPUs do not experience crashes.
- The **sensors monitor** surveys temperature sensors and related hardware readings when available, grouping them into logical categories (CPU, motherboard, etc.) and exposing them as a structured summary.

Each monitor's implementation is intentionally conservative in its use of system calls, preferring fewer, well-targeted queries at appropriate intervals rather than aggressive polling.

### 6.3.4 Widgets and the Application Layer

The visual presentation and user interaction logic are implemented in the `src/widgets/` package and the main application module `src/app.py`. Each major subsystem has a dedicated widget that is responsible for rendering metrics and responding to user input within its scope.

Widgets are typical Textual components: they compose text elements, progress bars, tables, and ASCII graphs (with the support of plotext) to present the metrics produced by their corresponding monitors. For example, the CPU widget might display a combined CPU usage bar, per-core mini-bars, and a time-series graph of aggregate utilization. The memory widget presents RAM and swap usage, while the process widget displays a paginated table with columns for PID, name, user, CPU percentage, and memory usage.

The `SystemMonitorApp` class in `src/app.py` orchestrates the layout and behavior of these widgets. It defines the overall structure of the interface using containers for each widget, along with a header and footer. The header typically displays the application name and a clock, while the footer provides help text and keybindings. Within `on_mount`, the app registers timers associated with the update intervals defined in the configuration; each timer periodically invokes the corresponding monitor's `collect()` method and triggers the associated widget to refresh its display.

User actions are handled through Textual's keybinding and event systems. Global actions such as quitting the application or forcing a refresh are implemented as methods on `SystemMonitorApp`, while more specific behaviors—like activating process search, changing pages, or initiating a kill operation—are implemented as methods and event handlers within the process widget. This design keeps the global application logic lean while allowing widgets to encapsulate their own interaction patterns.

### 6.3.5 Module Ownership and Evidence of Work

The project was implemented as a solo development effort. All major modules—utilities, configuration, monitors, widgets, and tests—were authored and maintained by the same developer. The Git history in the repository reflects this single-owner model, with commits grouped around the incremental build steps defined in the build plan.

Each of the core modules is associated with one or more commits that introduce, refine, and test its functionality. For example, the introduction of the `CircularBuffer` utility is followed by the addition of its corresponding test cases, and later by refinements based on integration with the monitors. Similarly, the creation of each monitor module is tracked alongside the development of its unit tests and the widget that consumes its data. This structured commit history serves as practical evidence of module ownership and the incremental, test-driven nature of the implementation.

## 6.4 System Integration Workflow

System integration proceeded in a controlled, stepwise manner that mirrored the structure of the build plan. Rather than attempting to wire all components together at once, the project followed a pattern of implementing a vertical slice of functionality and then integrating it with the existing system before moving on to the next slice.

Initial integration focused on connecting the core infrastructure: once the utility modules and configuration system were in place, the `BaseMonitor` class was introduced and validated independently. The next integration step involved creating the base Textual application canvas and confirming that it could run in isolation, rendering empty containers and responding to basic keybindings.

With this foundation established, the CPU monitor and widget were implemented and integrated end-to-end: the monitor collected metrics, the widget rendered them, and the application orchestrated the data flow and updates. This pattern was then repeated for memory, disk, network, processes, GPU, and sensors. At each stage, unit tests ensured the correctness of individual monitors and utilities, while integration tests validated that the application could start, render the relevant widgets, and respond to user input without errors.

Special attention was paid to the process management workflow, which involves more complex interactions between the monitor, widget, and user input. Here, integration testing confirmed that searching, pagination, and process termination behaved correctly and that permission or runtime errors were handled gracefully.

Throughout integration, automated tests were complemented by manual exploratory runs of the application, especially under different system loads and hardware configurations. This combination of automated and manual testing helped ensure that the final system behaved reliably as a cohesive whole.

## 6.5 Performance, Optimization, and Security Techniques

Performance and security considerations were integrated into the implementation phase rather than being treated as afterthoughts. The design and code of systop reflect a balance between responsiveness, resource efficiency, and safety.

On the performance side, the most significant decisions involve controlling update frequency and bounding resource usage. Each subsystem's update interval was chosen based on how quickly its metrics typically change: CPU, memory, and network are refreshed frequently to provide a real-time feel, while disk and sensors are updated less often to reduce overhead. These intervals are centralized in the configuration module, making it trivial to tune them for different environments.

The use of fixed-size `CircularBuffer` instances for historical data ensures that memory usage remains predictable even during long-running sessions. Sampling of metrics is structured to minimize redundant system calls; for example, cumulative counters are read once per interval and converted into rates by comparing against previous readings. On the rendering side, widgets avoid unnecessary recomputation and rely on Textual's efficient screen-diffing to keep redraw operations lightweight.

Security is addressed primarily through adherence to the principle of least privilege and careful error handling. The application is designed to run under normal user privileges without requiring elevated rights. Process termination operations are subject to the operating system's permission model; attempts to kill processes owned by other users or by the system result in informative error states rather than crashes. Metrics that might be restricted or unavailable (such as certain sensors or GPU statistics) are always accessed within `try/except` blocks, with fallbacks that present "not available" indicators in the interface instead of propagating exceptions to the user.

Equally important is the treatment of user and system data. The application does not send any information over the network and does not persist logs or snapshots by default. All monitoring is performed in-memory, and all data remains local to the running process. Combined with robust test coverage and an architecture that isolates risky operations in well-defined modules, these measures result in a tool that is both efficient in its resource usage and conservative in its security posture.
