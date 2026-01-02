# Chapter 5: System Design & Architecture

This chapter describes the overall design and architectural choices behind systop. It explains how the system is structured into layers and modules, how data flows between components, and how the internal "data model" and contracts were defined. It also highlights how security and performance concerns were addressed at the architectural level, before delving into implementation details.

## 5.1 Methodological Structure

At its core, systop is organized as a layered, modular system. This structure is a deliberate response to the complexity of real-time system monitoring: by clearly separating responsibilities, the design remains understandable, testable, and open to future extension.

The outermost layer is the presentation layer, implemented using the Textual framework. Here reside the main application class and the widgets that the user sees on screen. Their role is to render information, capture user input, and present a coherent, responsive interface. They do not, however, contain logic for querying the operating system or interpreting raw metrics. Instead, they depend on lower layers to supply structured data.

Beneath the presentation layer lies the domain logic layer, composed of monitor classes. Each monitor focuses on a specific area—CPU, memory, disk, network, processes, GPU, or sensors—and encapsulates the logic for collecting and structuring metrics in that area. All monitors inherit from a common base class, which defines shared behavior such as maintaining historical data and exposing a standard `collect()` method. This inheritance structure ensures that each monitor presents a consistent interface to the rest of the system, even though the underlying metrics may differ.

Supporting both of these layers is the infrastructure and utilities layer. This includes the circular buffer abstraction for time-series data, the formatting functions that convert numbers into meaningful human-readable strings, and the configuration system that centralizes tunable parameters. These utilities are intentionally generic; they are used by multiple monitors and widgets, but they do not depend on any one of them, which keeps coupling low and reusability high.

Finally, a testing and support layer spans the entire architecture. Unit tests, integration tests, and stability tests interact with the system much like a user or an integration would, verifying that the various layers behave as expected individually and in combination. Structuring the system in this way makes it straightforward to test, for example, a monitor in isolation with mocked system calls, or the full application using integration tests that simply start it and interact via its public interface.

Throughout the project, this layered architecture was developed incrementally. Each step in the build plan strengthened one part of the structure—adding a new monitor, fleshing out a widget, or extending the configuration—while preserving the integrity of the whole.

## 5.2 High-Level Architecture

Viewed from a high level, systop can be imagined as a pipeline that begins at the operating system and ends at the terminal interface. At one end, the Linux kernel and the `/proc` and `/sys` pseudo-filesystems expose raw metrics: CPU usage statistics, memory counters, disk and network I/O, process tables, and sensor readings. These are accessed not directly but through well-established Python libraries such as psutil, py-cpuinfo, and GPUtil, which provide a stable and portable API.

The monitor layer forms the next stage of the pipeline. Each monitor invokes the appropriate library functions, organizes the results into structured dictionaries, and stores selected values in its history buffer. The design emphasizes that monitors are the sole owners of system data collection; widgets never reach down to psutil or the kernel on their own. This separation is important both for correctness and for testability: by centralizing system calls, the project can mock or simulate them during testing.

Above the monitors is the application controller, implemented as a Textual application. It is responsible for coordinating the monitors and widgets. On startup, the application creates and arranges widgets in containers, sets up timers according to the configuration, and begins the event loop. Each timer is associated with a monitor and triggers a periodic call to its `collect()` method. The results are then forwarded to the appropriate widgets, which update their visual representation of the monitored subsystem.

The widgets form the final link in the chain to the user. Each widget receives a dictionary of metrics with well-known keys, transforms those values using the shared formatting utilities, and renders them using Textual and, where appropriate, ASCII plotting tools. This means that the semantics of each metric—its name, units, and typical range—are agreed upon between the monitor and widget, but the visual layout is the widget’s responsibility. This arrangement gives designers freedom to refine the interface without changing the data collection code.

The flow of control is correspondingly straightforward. User input, such as keypresses for quitting, searching processes, or navigating pages, enters at the application or widget level. In response, the application may query monitors, adjust state, or trigger redraws. Data always flows upward—from the system to libraries, to monitors, to the app, and finally to widgets—while commands and events flow downward from the user interface to the data layer.

## 5.3 Module Interactions in the Domain Context

Within the broader domain of system monitoring, systop occupies the niche of a real-time, interactive terminal application aimed at power users and developers. Its modules interact in ways that mirror the conceptual organization of that domain.

The operating system exposes a rich array of metrics: CPU utilization broken down by core and mode, physical and virtual memory usage, disk throughput, network bandwidth and packet counts, GPU load, and process information such as PID, user, CPU and memory usage, and status. Libraries such as psutil and GPUtil act as translators from this low-level representation into Python objects and dictionaries.

The monitors consume these library APIs and translate them into domain-specific views. For example, the CPU monitor not only reports overall utilization but also tracks per-core usage, load averages, and clock frequency. The disk monitor maps partitions to capacity and usage figures and converts cumulative I/O counters into per-second rates. The process monitor transforms a flat list of system processes into a paginated, sortable collection tailored for interactive browsing.

Widgets, in turn, interpret these domain views into visual structures: graphs of CPU usage over time, progress bars indicating memory saturation, tables listing processes with their resource footprint, or panels indicating GPU and sensor status. The application controller sits at the center of this web of interactions, ensuring that monitors are invoked at sensible intervals and that widgets receive timely updates while remaining responsive to user input.

Because each module has a clearly defined role, the system behaves predictably. Changing the sampling frequency of a monitor, for example, does not require changes to its widget; refining the rendering of a widget does not alter the underlying semantics of the metrics it displays. This modularity reflects the structure of the problem domain itself, where raw metrics, interpreted summaries, and presentations are distinct but closely related concepts.

## 5.4 In-Memory Data Model

Although systop does not employ a database in the traditional sense, it does rely on a consistent internal data model. This model is intentionally lightweight and entirely in-memory, optimized for responsiveness rather than persistence.

At the heart of the model are time-series buffers. Each monitor that presents historical data maintains one or more circular buffers into which it records successive samples of a particular metric. Because these buffers have a fixed maximum length, they act as a sliding window over recent history—typically on the order of sixty samples, corresponding to roughly one minute of data at a one-second update interval. This design allows the system to provide historical context in its visualizations without retaining unbounded amounts of data.

In addition to time-series data, each monitor tracks the latest snapshot of its metrics in a dictionary. These dictionaries act as structured, self-describing records: keys identify metrics (such as `overall_percent`, `per_core_percent`, `read_bytes_per_sec`, or `bytes_sent`), and values store the most recent reading. Widgets treat these dictionaries as read-only views, relying on their stability to simplify rendering logic.

Derived metrics—particularly rates such as bytes per second for disk or network I/O—are computed by comparing successive snapshots over the elapsed time interval. This approach avoids unnecessary complexity in the data model; it leverages the natural temporal ordering of samples and keeps calculations close to the monitors where the raw values originate. Formatting functions are applied as the final step before display, converting numeric values into strings with appropriate units and precision.

This in-memory, schema-light model is well-suited to a monitoring tool that is expected to run continuously without persisting data. It minimizes overhead while still providing enough structure to make the system easy to reason about and to test.

## 5.5 Internal Interfaces and Contracts

Even though systop does not expose a public API over the network, its internal interfaces are designed with the same rigor that one would apply to external contracts. The most important of these is the monitor interface. Through the `BaseMonitor` class, all monitors commit to providing a `collect()` method that returns a dictionary of metrics, to maintaining a history buffer, and to offering simple accessor methods for retrieving both history and the latest snapshot.

This contract means that the application and widgets can treat monitors polymorphically: they can schedule and invoke `collect()` on any monitor without needing to know the specifics of how that monitor gathers data. As long as the agreed-upon keys and types are respected, the rest of the system remains unaffected by internal implementation changes.

Widgets, similarly, adhere to an implicit contract: they accept dictionaries with documented keys and types, they use the shared formatting utilities to ensure consistent presentation, and they avoid mutating the data they receive. This keeps side effects localized and makes reasoning about data flow far simpler. Where user interactions are involved—for example, selecting a process or issuing a kill command—the widget translates the interaction into method calls or events directed at the appropriate subsystem.

The application controller defines a small set of actions that form the "user-to-system" interface. Actions like quitting the application, forcing a refresh, entering search mode, or changing pages are bound to key sequences and implemented as methods on the app or widgets. These methods, in turn, call into monitors or update local view state in predictable ways. Together, these internal contracts form a coherent, well-documented interface surface that could, if desired, be formalized into an external API at a later stage.

## 5.6 Security and Performance by Design

Many of systop’s security and performance properties are rooted in its architecture rather than in ad hoc implementation details. By design, the application runs under the privileges of the user who launches it and does not attempt to escalate those privileges. Process management operations, such as terminating a process, rely on the operating system’s permission checks, and failures due to insufficient rights are treated as normal outcomes that must be reported cleanly in the interface.

Data privacy is ensured by the simple fact that systop is entirely local: it does not open network connections, send telemetry, or write logs by default. All monitoring happens in-memory, and when the application exits, its state disappears with it. This greatly simplifies the threat model and reduces the risk of inadvertently exposing sensitive information about running processes or system configuration.

On the performance side, architectural decisions play an equally central role. By centralizing update intervals in the configuration module, the system can be tuned to match the capabilities of the host machine. Monitors are responsible for sampling metrics at those intervals and for doing so efficiently—batching psutil calls where possible and caching values to avoid redundant work. Widgets are designed to be lightweight clients of these metrics, re-rendering only when new data is available and relying on Textual’s efficient screen-diffing algorithm to minimize terminal updates.

The use of fixed-size circular buffers for history ensures that memory usage remains bounded even during long sessions. Because the application does not accumulate historical data indefinitely, there is no risk of gradual memory growth that might eventually impact system performance. Furthermore, the limited and well-defined set of system calls made by each monitor simplifies profiling and optimization: if performance issues are observed, they can be traced back to specific sampling or rendering operations.

Taken together, these design choices result in a system that is both robust and respectful of the host environment. Systop provides insight into system behavior without becoming a burden on the very resources it is designed to observe.
