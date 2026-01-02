# Chapter 3: Requirements & Team Workflow

This chapter formalizes what systop is required to do and under which constraints it must operate. It first presents detailed functional requirements, organized by feature area, that describe the expected behavior of the monitoring and process management capabilities from the user’s perspective. It then specifies non-functional requirements covering performance, reliability, usability, maintainability, portability, security, and environmental constraints. Finally, it discusses the technology choices and development constraints that shaped the project, along with the workflow used to structure and manage the work.

## 3.1 Functional Requirements

Functional requirements define what the system must do from a user's perspective. These requirements are organized by feature category.

### 3.1.1 System Monitoring Requirements

**FR-1: CPU Monitoring**
- The system shall display overall CPU utilization as a percentage
- The system shall display individual CPU core utilization for each logical processor
- The system shall show current, minimum, and maximum CPU frequencies
- The system shall display system load averages for 1, 5, and 15-minute intervals
- The system shall display CPU model and architecture information
- The system shall provide a historical graph of CPU usage over the last 60 seconds

**FR-2: Memory Monitoring**
- The system shall display total, used, free, and available RAM
- The system shall display RAM usage as both absolute values (GB) and percentages
- The system shall display swap memory total, used, and free
- The system shall provide historical graphs for RAM and swap usage
- The system shall update memory statistics every second

**FR-3: Disk Monitoring**
- The system shall display all mounted disk partitions
- The system shall show total, used, and free space for each partition
- The system shall display disk usage percentages for each partition
- The system shall monitor and display disk read/write operations per second
- The system shall show disk I/O throughput in MB/s
- The system shall provide historical graphs of disk I/O rates
- The system shall update disk statistics every 5 seconds

**FR-4: Network Monitoring**
- The system shall display upload and download speeds in real-time
- The system shall show total bytes sent and received since system boot
- The system shall display packet counts (sent and received)
- The system shall provide historical graphs of network bandwidth usage
- The system shall update network statistics every second

**FR-5: GPU Monitoring**
- The system shall detect NVIDIA GPU presence
- The system shall display GPU name, utilization percentage, and temperature
- The system shall show GPU memory usage (used/total)
- The system shall gracefully display "N/A" when GPU is not available
- The system shall update GPU statistics every 2 seconds

**FR-6: Temperature Sensor Monitoring**
- The system shall detect available hardware temperature sensors
- The system shall display current, high, and critical temperatures for each sensor
- The system shall group sensors by type (CPU, motherboard, etc.)
- The system shall hide the temperature section when no sensors are available
- The system shall update temperature readings every 5 seconds

### 3.1.2 Process Management Requirements

**FR-7: Process Display**
- The system shall display a list of all running processes
- The system shall show process ID (PID), name, owner, CPU usage, memory usage, and status
- The system shall support sorting by any column (CPU%, memory%, name, PID)
- The system shall display process memory usage in both percentage and MB
- The system shall update process list every 2 seconds

**FR-8: Process Navigation**
- The system shall implement pagination with configurable page size (default: 20 processes)
- The system shall support keyboard navigation (arrow keys, Page Up/Down)
- The system shall visually highlight the currently selected process
- The system shall display current page number and total pages

**FR-9: Process Search**
- The system shall provide a search function activated by the '/' key
- The system shall filter processes by name in real-time as the user types
- The system shall support case-insensitive search
- The system shall allow clearing search with the Escape key
- The system shall reset to page 1 when a new search is performed

**FR-10: Process Control**
- The system shall allow users to terminate selected processes
- The system shall require confirmation before killing a process
- The system shall display success or error messages after kill attempts
- The system shall handle permission-denied errors gracefully
- The system shall support killing processes using the 'k' key

### 3.1.3 User Interface Requirements

**FR-11: Layout and Organization**
- The system shall organize information in clearly separated sections
- The system shall display a header with application name and current time
- The system shall display a footer with available keybindings
- The system shall support scrolling for content exceeding terminal height
- The system shall maintain consistent visual styling across all sections

**FR-12: Real-time Updates**
- The system shall update all displayed metrics in real-time without user intervention
- The system shall use appropriate update intervals per metric type
- The system shall not block user interaction during updates
- The system shall maintain smooth animations and transitions

**FR-13: Interactive Controls**
- The system shall respond to keyboard input for all interactive features
- The system shall support the following global keybindings:
  - 'q': Quit application
  - 'r': Force refresh all widgets
- The system shall support process-specific keybindings when process widget is focused
- The system shall provide visual feedback for user actions

**FR-14: Data Visualization**
- The system shall display historical data as ASCII line graphs
- The system shall use progress bars for percentage-based metrics
- The system shall employ color coding to highlight important information
- The system shall format numerical values with appropriate units (KB, MB, GB, GHz, etc.)

### 3.1.4 System Behavior Requirements

**FR-15: Startup and Shutdown**
- The system shall start within 2 seconds on typical hardware
- The system shall initialize all monitoring modules on startup
- The system shall perform graceful shutdown, cleaning up resources
- The system shall not leave orphaned processes after exit

**FR-16: Error Handling**
- The system shall not crash when encountering monitoring errors
- The system shall log errors appropriately for debugging
- The system shall display user-friendly error messages
- The system shall continue operating when individual widgets fail

**FR-17: Hardware Compatibility**
- The system shall detect and adapt to available hardware
- The system shall work correctly on systems without GPUs
- The system shall work correctly on systems without temperature sensors
- The system shall handle varying numbers of CPU cores (1 to 256+)
- The system shall support various network interface configurations

## 3.2 Non-functional Requirements

Non-functional requirements specify quality attributes and constraints on how the system operates.

### 3.2.1 Performance Requirements

**NFR-1: Resource Efficiency**
- The system shall consume less than 100 MB of memory during normal operation
- The system shall use less than 5% CPU when the system is idle
- The system shall not cause observable system slowdown
- The system shall not leak memory during extended operation (24+ hours)

**NFR-2: Responsiveness**
- The system shall respond to user input within 100 milliseconds
- The system shall maintain a consistent frame rate of at least 10 FPS for graph updates
- The system shall not freeze or become unresponsive during data collection
- Process list scrolling shall be smooth without noticeable lag

**NFR-3: Update Intervals**
- CPU and memory metrics shall update every 1 second
- Network metrics shall update every 1 second
- Disk metrics shall update every 5 seconds
- GPU metrics shall update every 2 seconds
- Temperature metrics shall update every 5 seconds
- Process list shall update every 2 seconds

**NFR-4: Scalability**
- The system shall handle up to 10,000 concurrent processes without performance degradation
- The system shall support up to 256 CPU cores
- The system shall handle up to 100 mounted disk partitions
- Historical data buffers shall not grow unbounded (60-second circular buffers)

### 3.2.2 Reliability Requirements

**NFR-5: Stability**
- The system shall run continuously for 24+ hours without crashes
- The system shall maintain accuracy of displayed metrics (±2% variance acceptable)
- The system shall recover gracefully from transient system call failures
- The system shall maintain data integrity during high system load

**NFR-6: Fault Tolerance**
- Individual widget failures shall not crash the entire application
- Missing hardware (GPU, sensors) shall not cause errors or warnings
- Permission-denied errors shall be handled without disruption
- Network interface changes shall be detected and adapted to

**NFR-7: Data Accuracy**
- CPU usage percentages shall be accurate within ±1%
- Memory values shall be accurate to the byte (as provided by OS)
- Disk and network rates shall be calculated with proper timing precision
- Process information shall reflect actual system state with <2 second latency

### 3.2.3 Usability Requirements

**NFR-8: Learnability**
- New users shall be able to understand the basic interface within 30 seconds
- All keybindings shall be documented in the footer or help screen
- The interface shall follow common TUI conventions
- Visual hierarchy shall make important information immediately apparent

**NFR-9: Accessibility**
- The system shall work in terminals with minimum 80x24 character dimensions
- The system shall be usable with keyboard only (no mouse required)
- Color coding shall not be the only means of conveying information
- Text shall be readable with appropriate contrast

**NFR-10: Consistency**
- All widgets shall follow the same visual styling conventions
- Keybindings shall be consistent across the application
- Numerical formatting shall be uniform throughout
- Update animations shall have consistent timing

### 3.2.4 Maintainability Requirements

**NFR-11: Code Quality**
- Code shall follow PEP 8 Python style guidelines
- All public functions and classes shall have docstrings
- Cyclomatic complexity shall be kept below 10 for individual functions
- Code duplication shall be minimized through appropriate abstraction

**NFR-12: Testability**
- Test coverage shall exceed 80% for monitor and utility modules
- All monitoring functions shall be unit tested with mocked system calls
- Integration tests shall verify application startup and basic operation
- Tests shall execute in under 10 seconds on typical hardware

**NFR-13: Modularity**
- Each monitoring module shall be independent and self-contained
- New monitors shall be addable without modifying existing code (Open/Closed Principle)
- Widgets shall be decoupled from data collection logic
- Configuration shall be centralized in a single module

**NFR-14: Documentation**
- README shall provide complete installation and usage instructions
- Code shall include inline comments for complex logic
- Architecture shall be documented with clear diagrams
- API documentation shall be generated from docstrings

### 3.2.5 Portability Requirements

**NFR-15: Platform Support**
- The system shall run on Linux kernel 4.x and above
- The system shall support Python 3.10, 3.11, 3.12, and 3.13
- The system shall work in common terminal emulators (gnome-terminal, kitty, alacritty, etc.)
- The system shall function over SSH connections without graphical requirements

**NFR-16: Dependency Management**
- All dependencies shall be specified with version constraints
- Dependencies shall be installable via pip from PyPI
- The system shall have no compiled dependencies requiring system libraries
- Dependency updates shall not break existing functionality

### 3.2.6 Security Requirements

**NFR-17: Process Management Security**
- The system shall respect OS-level permissions for process operations
- Users shall only be able to kill processes they own (or with appropriate privileges)
- The system shall not expose sensitive information from processes owned by other users
- Error messages shall not leak system information that could aid attackers

**NFR-18: Data Privacy**
- The system shall not transmit any data over the network
- The system shall not log sensitive information (passwords, tokens)
- The system shall not write any persistent data to disk
- All data shall remain local to the running process

## 3.3 System Constraints

System constraints define the boundaries within which the system must operate.

### 3.3.1 Hardware Constraints

**HC-1: Minimum Hardware Requirements**
- Processor: Any x86-64 or ARM64 processor with at least 1 core
- Memory: Minimum 512 MB RAM available for the application
- Disk: 50 MB for installation (including dependencies)
- Display: Terminal with minimum 80x24 character display
- GPU (optional): NVIDIA GPU with nvidia-smi available for GPU monitoring

**HC-2: Recommended Hardware**
- Processor: Multi-core CPU for better monitoring of parallel workloads
- Memory: 2+ GB RAM for comfortable operation with many processes
- Display: Terminal with 120x40+ character display for optimal layout
- Network: Any network interface for network monitoring

**HC-3: Hardware Limitations**
- GPU monitoring is limited to NVIDIA GPUs (AMD/Intel not supported)
- Temperature sensors require kernel support and appropriate permissions
- Some virtualized environments may not expose all metrics
- Container environments may have restricted access to system information

### 3.3.2 Software Constraints

**SC-1: Operating System**
- Primary support: Linux (Ubuntu 20.04+, Fedora 35+, Arch, Debian 11+)
- Kernel version: Linux 4.x or higher
- File systems: Requires /proc and /sys pseudo-filesystems
- Not supported: Windows, macOS (though psutil is cross-platform, testing was Linux-only)

**SC-2: Python Environment**
- Python version: 3.10 or higher required
- Virtual environment: Recommended for isolation
- Package manager: pip required for dependency installation
- Not supported: Python 2.x, Python 3.9 and below

**SC-3: Dependencies**
- textual >= 0.50.0 (TUI framework)
- psutil >= 5.9.0 (system monitoring)
- plotext >= 5.2.0 (ASCII plotting)
- py-cpuinfo >= 9.0.0 (CPU information)
- GPUtil >= 1.4.0 (GPU monitoring)
- pytest >= 7.4.0 (testing, development only)

**SC-4: Terminal Requirements**
- Terminal emulator with ANSI color support
- UTF-8 encoding support for proper character rendering
- Minimum terminal size: 80x24 characters
- Terminal multiplexers (tmux, screen) supported but may have rendering quirks

### 3.3.3 Environmental Constraints

**EC-1: Deployment Environment**
- The system runs as a user-space application (no root required for basic features)
- Process killing may require appropriate permissions
- Temperature sensor access may require user to be in specific groups (e.g., `lm-sensors`)
- GPU monitoring requires nvidia-smi to be in PATH

**EC-2: Network Constraints**
- No network connectivity required for operation
- All monitoring is local to the host system
- Can be used over SSH connections
- No external API calls or data transmission

**EC-3: Development Environment**
- Development requires Linux system or Linux VM
- Git for version control
- Fish shell recommended (development was done with fish)
- VS Code or similar IDE recommended for development

### 3.3.4 Legal and Licensing Constraints

**LC-1: Open Source Compliance**
- The project uses MIT License (permissive)
- All dependencies are open source with compatible licenses
- No proprietary code or libraries used
- Attribution required for Textual, psutil, and other libraries

**LC-2: Usage Restrictions**
- The system monitors only publicly accessible system information
- No circumvention of OS security mechanisms
- Respects user permissions and access controls
- No warranty or liability as per MIT License terms

### 3.3.5 Development Constraints

**DC-1: Time Constraints**
- Development organized into 16 incremental steps
- Each step designed to be completable independently
- Estimated 40-60 hours total development time
- Testing and documentation included in timeline

**DC-2: Resource Constraints**
- Individual developer project (solo development)
- Limited to Python ecosystem and available libraries
- No budget for proprietary tools or services
- Community support through documentation for future contributors

**DC-3: Knowledge Constraints**
- Requires understanding of Linux system programming
- Familiarity with Python asynchronous programming
- Knowledge of TUI frameworks (Textual)
- Understanding of system monitoring concepts

## 3.4 Technology Stack Justification

This section explains the rationale behind selecting specific technologies for the project.

### 3.4.1 Programming Language: Python 3.13

**Selection: Python**

**Justification:**
- **Rapid Development**: Python's expressive syntax and extensive standard library enable faster development compared to C/C++
- **Rich Ecosystem**: Excellent libraries available (psutil, Textual) for system monitoring and TUI development
- **Maintainability**: Clear, readable code that's easier to maintain and extend
- **Cross-platform Potential**: While targeting Linux, Python/psutil provide cross-platform capabilities for future expansion
- **Testing Support**: Excellent testing frameworks (pytest) and mocking capabilities

**Trade-offs Accepted:**
- **Performance Overhead**: Python is slower than C/C++ but monitoring tasks are I/O-bound rather than CPU-bound
- **Memory Footprint**: Higher memory usage (~50-80 MB vs ~10-20 MB for C) but acceptable for the use case
- **Distribution Size**: Requires Python runtime but this is standard on Linux systems

**Alternatives Considered:**
- **C/C++**: Better performance but significantly longer development time, harder to maintain
- **Rust**: Excellent performance and safety but steeper learning curve, fewer TUI libraries
- **Go**: Good performance, good standard library, but less mature TUI ecosystem

### 3.4.2 TUI Framework: Textual

**Selection: Textual v0.50.0+**

**Justification:**
- **Modern Architecture**: Reactive programming model inspired by web frameworks (React-like)
- **Rich Widget Library**: Pre-built components for common UI patterns
- **CSS-like Styling**: Familiar styling approach for developers with web background
- **Async/Await Support**: Native asynchronous programming for responsive interfaces
- **Active Development**: Regular updates, active community, good documentation
- **Developer Experience**: Excellent debugging tools and error messages

**Trade-offs Accepted:**
- **Framework Dependency**: Tightly coupled to Textual (but provides significant value)
- **Younger Framework**: Less mature than urwid but rapidly improving
- **Learning Curve**: Reactive paradigm requires understanding new concepts

**Alternatives Considered:**
- **urwid**: More mature but older API, more complex for similar results
- **blessed**: Too low-level, would require building more infrastructure
- **Rich (standalone)**: Excellent for output but not designed for interactive TUI apps
- **curses**: Python's built-in but very low-level and platform-specific quirks

### 3.4.3 System Monitoring: psutil

**Selection: psutil v5.9.0+**

**Justification:**
- **Comprehensive Coverage**: Provides CPU, memory, disk, network, and process information
- **Cross-platform**: Works on Linux, Windows, macOS (future-proofing)
- **Well-maintained**: Long history (since 2009), actively maintained, stable API
- **Pythonic API**: Clean, intuitive interface consistent with Python conventions
- **Widely Used**: Battle-tested in production environments, extensive real-world usage
- **Good Documentation**: Excellent documentation with examples

**Trade-offs Accepted:**
- **Abstraction Layer**: Slightly less direct than native system calls but more portable
- **Update Latency**: May be slightly slower than direct /proc reads but negligible

**Alternatives Considered:**
- **Direct /proc Reads**: More control but Linux-specific, more code, error-prone
- **os/subprocess Calls**: Too low-level, would need to parse command output
- **platform-specific Libraries**: Would limit portability

### 3.4.4 GPU Monitoring: GPUtil

**Selection: GPUtil v1.4.0+**

**Justification:**
- **Simple API**: Straightforward interface for NVIDIA GPU monitoring
- **Lightweight**: Minimal overhead, simple wrapper around nvidia-smi
- **Sufficient Features**: Provides essential metrics (utilization, memory, temperature)
- **Easy Integration**: Works well with psutil and existing architecture

**Limitations Accepted:**
- **NVIDIA Only**: Does not support AMD or Intel GPUs (acceptable for initial version)
- **Requires nvidia-smi**: Additional dependency but standard on NVIDIA setups

**Alternatives Considered:**
- **pynvml**: More comprehensive but more complex API
- **py3nvml**: Similar to pynvml, more features than needed
- **Direct nvidia-smi calls**: Would require parsing output, less reliable

### 3.4.5 Visualization: plotext

**Selection: plotext v5.2.0+**

**Justification:**
- **ASCII Plotting**: Creates plots using terminal characters
- **Simple API**: Easy to integrate for line graphs
- **Textual Compatible**: Works within Textual widgets
- **Lightweight**: Minimal dependencies and overhead

**Trade-offs Accepted:**
- **Limited Plot Types**: Focus on line graphs (sufficient for time-series data)
- **Resolution Limits**: Character-based resolution is inherent limitation

**Alternatives Considered:**
- **asciichartpy**: Similar capability but less feature-rich
- **Custom Implementation**: Would take significant time for similar results
- **No Graphs**: Would reduce visual appeal significantly

### 3.4.6 CPU Information: py-cpuinfo

**Selection: py-cpuinfo v9.0.0+**

**Justification:**
- **Detailed CPU Info**: Provides model name, architecture, features
- **Pure Python**: No compiled dependencies
- **Complements psutil**: Fills gap in CPU metadata not provided by psutil
- **Cross-platform**: Works consistently across systems

**Trade-offs Accepted:**
- **Additional Dependency**: Another package to maintain but small footprint

**Alternatives Considered:**
- **Reading /proc/cpuinfo**: Linux-specific, would need parsing logic
- **cpuinfo via psutil**: psutil provides less detailed CPU information

### 3.4.7 Testing Framework: pytest

**Selection: pytest v7.4.0+**

**Justification:**
- **Industry Standard**: Most popular Python testing framework
- **Rich Plugin Ecosystem**: pytest-asyncio for async testing, pytest-cov for coverage
- **Simple Syntax**: Minimal boilerplate, clear test structure
- **Powerful Features**: Fixtures, parametrization, comprehensive assertion introspection
- **Excellent Mocking**: Easy to mock psutil and other dependencies

**Alternatives Considered:**
- **unittest**: Python's built-in but more verbose, less feature-rich
- **nose2**: Less active development than pytest

### 3.4.8 Development Tools

**Version Control: Git**
- Industry standard, excellent branching and merging
- GitHub for hosting and collaboration

**Shell: Fish**
- User-friendly, good auto-completion
- Used during development (project supports any shell)

**Virtual Environment: venv**
- Python's built-in virtual environment tool
- Simple, reliable, no additional dependencies

**Code Quality:**
- **PEP 8**: Python style guide for consistent formatting
- **Type Hints**: Python 3.10+ type annotations for better code clarity
- **Docstrings**: Google-style docstrings for documentation

### 3.4.9 Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.13 | Core programming language |
| TUI Framework | Textual | ≥0.50.0 | User interface framework |
| System Monitoring | psutil | ≥5.9.0 | Core system metrics |
| GPU Monitoring | GPUtil | ≥1.4.0 | NVIDIA GPU metrics |
| CPU Info | py-cpuinfo | ≥9.0.0 | Detailed CPU information |
| Visualization | plotext | ≥5.2.0 | ASCII charts and graphs |
| Testing | pytest | ≥7.4.0 | Unit and integration testing |
| Async Testing | pytest-asyncio | ≥0.21.0 | Asynchronous test support |
| Version Control | Git | Any | Source code management |

**Dependency Philosophy:**
- Prefer mature, well-maintained libraries
- Avoid unnecessary dependencies
- Use pure-Python packages when possible
- Ensure compatibility with Python 3.10+

## 3.5 Team Structure & Individual Responsibilities

**Project Type: Individual Development**

This project was completed as an individual effort, with all roles and responsibilities handled by a single developer. However, the work was structured and organized as if managing a team, with clear role definitions and responsibilities.

### 3.5.1 Roles Undertaken

**Role 1: Project Architect**
- **Responsibilities:**
  - Designed overall system architecture
  - Made technology stack decisions
  - Created modular design with base classes
  - Defined monitor-widget-app separation pattern
  - Documented architecture in BUILD_PLAN.md

- **Deliverables:**
  - System architecture documentation
  - Component interaction diagrams
  - Technology justification document
  - Extensibility patterns

**Role 2: Backend Developer (Monitors)**
- **Responsibilities:**
  - Implemented all monitor modules (CPU, memory, disk, network, GPU, sensors, processes)
  - Developed BaseMonitor abstract class
  - Created data collection logic using psutil
  - Implemented rate calculation for network and disk I/O
  - Handled hardware detection and graceful fallbacks

- **Deliverables:**
  - src/monitors/base.py
  - src/monitors/cpu.py
  - src/monitors/memory.py
  - src/monitors/disk.py
  - src/monitors/network.py
  - src/monitors/gpu.py
  - src/monitors/sensors.py
  - src/monitors/processes.py

**Role 3: Frontend Developer (Widgets)**
- **Responsibilities:**
  - Designed and implemented all widget components
  - Created real-time visualization with plotext
  - Implemented reactive UI updates using Textual
  - Developed process management interface with search and pagination
  - Ensured consistent visual styling

- **Deliverables:**
  - src/widgets/cpu_widget.py
  - src/widgets/memory_widget.py
  - src/widgets/disk_widget.py
  - src/widgets/network_widget.py
  - src/widgets/gpu_widget.py
  - src/widgets/sensors_widget.py
  - src/widgets/process_widget.py

**Role 4: Application Integrator**
- **Responsibilities:**
  - Built main application orchestration (src/app.py)
  - Integrated all widgets into cohesive interface
  - Managed update scheduling and timers
  - Implemented graceful shutdown and error handling
  - Created configuration system

- **Deliverables:**
  - src/app.py (main application)
  - src/config.py (configuration)
  - main.py (entry point)
  - Integration and coordination logic

**Role 5: Utilities Developer**
- **Responsibilities:**
  - Created reusable utility functions
  - Implemented circular buffer for historical data
  - Developed formatting functions for display
  - Built helper classes and common functionality

- **Deliverables:**
  - src/utils/history.py (circular buffer)
  - src/utils/formatters.py (display formatting)

**Role 6: Quality Assurance Engineer**
- **Responsibilities:**
  - Designed testing strategy
  - Wrote unit tests for all monitors and utilities
  - Created integration tests
  - Performed manual testing
  - Verified coverage metrics (>80%)

- **Deliverables:**
  - tests/test_utils/test_formatters.py
  - tests/test_utils/test_history.py
  - tests/test_monitors/test_*.py (all monitor tests)
  - tests/test_integration.py

**Role 7: Documentation Specialist**
- **Responsibilities:**
  - Wrote comprehensive README
  - Created BUILD_PLAN.md (16-step development guide)
  - Created AGENT_PROMPTS.md (incremental prompts)
  - Added code docstrings and comments
  - Prepared project report

- **Deliverables:**
  - README.md
  - BUILD_PLAN.md
  - AGENT_PROMPTS.md
  - Code documentation
  - This report

### 3.5.2 Work Distribution Timeline

The work was organized into 16 distinct phases, each focusing on specific deliverables:

| Phase | Focus Area | Estimated Hours | Components Delivered |
|-------|------------|-----------------|---------------------|
| 1 | Project Setup | 2h | Dependencies, environment setup |
| 2 | Utilities | 4h | Formatters, circular buffer, tests |
| 3 | Configuration | 1h | Config system |
| 4 | Base Monitor | 2h | Abstract base class |
| 5 | Base Canvas | 3h | Main app structure, layout |
| 6 | CPU Module | 5h | CPU monitor + widget + tests |
| 7 | Memory Module | 4h | Memory monitor + widget + tests |
| 8 | Disk Module | 5h | Disk monitor + widget + tests |
| 9 | Network Module | 4h | Network monitor + widget + tests |
| 10 | GPU Module | 4h | GPU monitor + widget + tests |
| 11 | Sensors Module | 3h | Sensors monitor + widget + tests |
| 12 | Process Module | 8h | Complex process management + tests |
| 13 | Polish & Integration | 4h | Error handling, optimization |
| 14 | Testing Suite | 3h | Integration tests, coverage verification |
| 15 | Documentation | 4h | README, docstrings |
| 16 | Final Verification | 3h | End-to-end testing, validation |
| **Total** | **All Components** | **~59 hours** | **Complete Application** |

### 3.5.3 Skills Applied

The project required applying diverse skills across multiple domains:

**System Programming:**
- Understanding Linux system metrics and /proc filesystem
- Process management and signals
- System call interfaces via psutil
- Hardware detection and capability queries

**Software Engineering:**
- Object-oriented design and inheritance
- Design patterns (MVC, Factory, Template Method)
- Separation of concerns
- Code organization and modularity

**Python Development:**
- Async/await and asynchronous programming
- Reactive programming with Textual
- Type hints and modern Python features
- Testing with pytest and mocking

**User Interface Design:**
- TUI layout and organization
- Information hierarchy and visual design
- Interaction patterns and keybindings
- Real-time visualization

**Testing and Quality Assurance:**
- Unit testing with mocked dependencies
- Integration testing for TUI apps
- Test-driven development practices
- Coverage analysis

**Documentation:**
- Technical writing
- Code documentation with docstrings
- User-facing documentation (README)
- Development process documentation

## 3.6 Collaboration Workflow

While this is an individual project, a structured workflow was essential for organized development. The workflow simulates best practices from team development.

### 3.6.1 Development Methodology

**Incremental Development Approach:**

The project followed a structured, incremental development methodology documented in BUILD_PLAN.md and AGENT_PROMPTS.md. This approach breaks the complex project into 16 manageable steps, each building on the previous one.

**Methodology Characteristics:**
- **Sequential Progression**: Each step completes before moving to the next
- **Clear Milestones**: Each step has defined deliverables and acceptance criteria
- **Testable Increments**: Each module is tested independently
- **Integration Points**: Regular integration after each module
- **Documentation-Driven**: Each step has detailed specifications

### 3.6.2 Step-by-Step Workflow

The development followed this systematic process for each of the 16 steps:

```
Step N: [Feature Name]
├── 1. Read Specification
│   └── Review BUILD_PLAN.md for detailed requirements
│
├── 2. Implement Component
│   ├── Create monitor class (if applicable)
│   ├── Create widget class (if applicable)
│   └── Implement core functionality
│
├── 3. Write Tests
│   ├── Unit tests with mocked dependencies
│   ├── Test edge cases and error conditions
│   └── Verify test passes: pytest tests/
│
├── 4. Integrate
│   ├── Import into main application
│   ├── Mount widget to appropriate container
│   └── Verify integration
│
├── 5. Manual Testing
│   ├── Run application: python main.py
│   ├── Verify feature works correctly
│   └── Test interaction with existing features
│
├── 6. Documentation
│   ├── Add/update docstrings
│   ├── Update README if needed
│   └── Document any issues or limitations
│
└── 7. Commit
    └── Git commit with clear message describing changes
```

### 3.6.3 Task Organization

Tasks were organized using the AGENT_PROMPTS.md file, which served as a virtual task board:

**Structure:**
- **16 Major Tasks**: One per development step
- **Each Task Contains**:
  - Project context and prerequisites
  - Current status and objectives
  - Detailed subtasks
  - Deliverables checklist
  - Testing requirements
  - Acceptance criteria

**Example Task Breakdown (Step 6: CPU Module):**

```markdown
PROJECT CONTEXT:
- Location, environment, dependencies

PREREQUISITES:
✅ Dependencies installed
✅ Utils working
✅ Base monitor exists
✅ Base app canvas working

YOUR TASKS:
1. Create src/monitors/cpu.py
   - CPUMonitor class
   - collect() method
   - [detailed specifications]

2. Create src/widgets/cpu_widget.py
   - CPUWidget class
   - render() method
   - [detailed specifications]

3. Integration in src/app.py
   - [integration steps]

4. Create tests/test_monitors/test_cpu.py
   - [test requirements]

5. Manual testing
   - [testing checklist]

DELIVERABLES:
☐ src/monitors/cpu.py implemented
☐ src/widgets/cpu_widget.py implemented
☐ Integration complete
☐ Tests passing
☐ Manual verification successful
```

### 3.6.4 Version Control Workflow

**Git Usage:**
- **Repository**: Local git repository initialized at project start
- **Branch Strategy**: Main branch (linear development)
- **Commit Frequency**: After each completed step
- **Commit Messages**: Descriptive, following convention:
  ```
  feat: Add CPU monitoring module with per-core graphs
  test: Add unit tests for CPU monitor
  fix: Handle missing GPU gracefully
  docs: Update README with keybindings
  refactor: Extract common widget patterns to base class
  ```

**Commit Milestones:**
```
1. chore: Initialize project structure and dependencies
2. feat: Add utility modules (formatters, circular buffer)
3. feat: Add configuration system
4. feat: Add base monitor abstract class
5. feat: Create base application canvas
6. feat: Implement CPU monitoring module
7. feat: Implement memory monitoring module
8. feat: Implement disk monitoring module
9. feat: Implement network monitoring module
10. feat: Add GPU monitoring with fallback
11. feat: Add temperature sensor monitoring
12. feat: Implement process management with search and kill
13. refactor: Polish integration and error handling
14. test: Complete testing suite with integration tests
15. docs: Add comprehensive documentation
16. test: Final verification and acceptance testing
```

### 3.6.5 Quality Gates

Each step required passing quality gates before proceeding:

**Quality Gate Checklist:**
- ✅ **Code Complete**: All required files created
- ✅ **Functionality Verified**: Manual testing confirms feature works
- ✅ **Tests Pass**: `pytest tests/ -v` shows all green
- ✅ **No Regressions**: Existing features still work
- ✅ **Documentation Updated**: Docstrings and comments added
- ✅ **Code Style**: PEP 8 compliant
- ✅ **Integration Clean**: No errors or warnings on startup

### 3.6.6 Development Tools

**IDE/Editor:**
- VS Code with Python extensions
- Pylance for type checking and IntelliSense
- Python Test Explorer for running tests

**Terminal:**
- Fish shell for development
- Multiple terminal tabs for:
  - Running the application
  - Running tests
  - Monitoring system resources
  - Git operations

**Testing:**
- pytest for running tests
- pytest-cov for coverage reports
- Manual testing in terminal

**Documentation:**
- Markdown for all documentation
- Docstrings in code
- Comments for complex logic

### 3.6.7 AI-Assisted Development

**Note on Development Approach:**

This project leveraged AI assistance (GitHub Copilot and AI chat) as a development tool:

**AI Role:**
- Code generation assistance
- Test generation
- Documentation drafting
- Problem-solving discussions
- Architecture validation

**Developer Role:**
- System design and architecture decisions
- Requirement definition
- Code review and refinement
- Integration and testing
- Quality assurance
- Final verification

The AI acted as a productivity multiplier, similar to using advanced IDE features, Stack Overflow, or pair programming, but the developer maintained full control over design, implementation choices, and quality standards.

### 3.6.8 Workflow Summary

**Key Success Factors:**

1. **Structured Approach**: Clear step-by-step plan (BUILD_PLAN.md)
2. **Incremental Progress**: Small, testable increments
3. **Quality Focus**: Testing and verification at each step
4. **Documentation**: Continuous documentation throughout
5. **Isolation**: Each module developed independently
6. **Integration**: Regular integration prevents big-bang issues
7. **Feedback Loop**: Manual testing provides immediate feedback

**Lessons Learned:**

- Breaking complex projects into small steps makes them manageable
- Testing early and often prevents compound bugs
- Clear documentation helps maintain momentum
- Modular architecture enables independent development
- Regular integration catches compatibility issues early

---

This chapter has established the comprehensive requirements (functional and non-functional), constraints, technology choices, and development workflow for the systop project. The structured approach to individual development demonstrates how software engineering best practices can be applied even in solo projects to achieve professional results.
