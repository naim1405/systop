# Chapter 7: Testing, Results, and Evaluation

This chapter evaluates the systop application from the perspective of verification and validation. It describes the testing strategy adopted during development, summarizes representative test cases and outcomes, and discusses the performance characteristics observed during execution. It then compares systop qualitatively against established system monitoring tools, and concludes with a narrative of execution results and guidance on how screenshots and demonstrations can be integrated into the final report.

## 7.1 Testing Strategy

Testing for systop followed a layered strategy aligned with the system’s architecture and the project’s quality objectives. The primary goal was to ensure that each module behaved correctly in isolation and that, when combined, the system exhibited stable and predictable behavior under realistic workloads.

At the lowest level, **unit testing** was used extensively for utility modules and monitors. The `src/utils/` package—particularly `history.py` and `formatters.py`—was covered by focused unit tests exercising boundary conditions (such as buffer overflows, zero and negative values, and large numbers). Similarly, each monitor in `src/monitors/` was tested with mocked psutil and related library calls, allowing verification of data shaping, error handling, and history updates without depending on the actual state of the host system.

Above the unit level, **integration tests** were introduced to validate that the monitors, widgets, and main application could operate together. These tests started the application in a controlled environment and verified that it could import all modules, instantiate the `SystemMonitorApp`, and render the initial layout without raising exceptions. Integration tests also checked that key widgets—such as CPU, memory, disk, and network—could receive and display mock data as expected.

While a full **system testing** campaign was beyond the scope of automated tooling alone, manual exploratory tests played a complementary role. Running `python main.py` on actual Linux systems allowed the developer to observe live behavior: graphs updating over time, widgets responding to user input, and error conditions (such as missing GPUs or sensors) being handled gracefully. These manual tests provided confidence that the application behaved as specified in realistic scenarios.

A subset of tests also served as informal **acceptance tests**, verifying that the system met the high-level criteria articulated in the requirements and build plan. The final automated test run—covering all tests in the `tests/` directory—completed successfully with 142 tests passing and no failures, and code coverage measurements indicated strong coverage of the core logic.

## 7.2 Representative Test Cases

The full test suite is too extensive to reproduce in its entirety in this report, but several representative test cases illustrate the breadth and depth of verification performed. The tables below summarize selected examples from utilities, monitors, and the integration layer.

### 7.2.1 Utility Functions

| Test Case | Input | Expected Output | Actual Result |
|----------|-------|-----------------|---------------|
| `format_bytes` with small value | 1536 bytes | "1.50 KB" | Matches expected string formatting |
| `format_bytes` with large value | 1073741824 bytes | "1.00 GB" | Correct scaling and units |
| `format_percentage` normal value | 45.67 | "45.7%" (1 decimal place) | Correct rounding and suffix |
| `format_uptime` | 3665 seconds | "1h 1m 5s" | Correct decomposition of time |
| `CircularBuffer` overflow | Append 70 values to maxsize=60 | Buffer contains last 60 values only | Size bounded, oldest values discarded |

These tests confirm that the foundational utilities behave deterministically and handle edge cases gracefully, which is essential for consistent presentation in the user interface.

### 7.2.2 Monitor Modules

| Monitor | Scenario | Expected Behavior | Actual Result |
|---------|----------|-------------------|---------------|
| CPU monitor | psutil returns per-core utilizations | `collect()` returns `overall_percent` and matching `per_core_percent` list | Structure and types verified via unit tests |
| Memory monitor | psutil reports RAM and swap stats | Snapshot includes total, used, free, available, and percentages | Keys and value ranges verified |
| Disk monitor | Simulated partitions and I/O counters | Snapshot lists partitions with usage and read/write rates | Correct rate computation from successive samples |
| Network monitor | Simulated network traffic counters | Snapshot shows upload/download speeds and cumulative bytes | Deltas over interval computed correctly |
| Process monitor | Mocked process list | Snapshot contains PID, name, user, CPU%, memory% for each process | Sorting and pagination logic validated |

These monitor tests rely heavily on mocking to simulate system states that would be difficult to reproduce reliably on a developer machine (for example, high disk activity or thousands of processes). By focusing on structure and transformation rather than specific numeric values, they ensure that the monitors’ contracts are upheld.

### 7.2.3 Integration and Application

| Test | Description | Expected Outcome | Actual Result |
|------|-------------|------------------|---------------|
| `test_integration.py` | Start the app and verify basic startup | Application imports successfully and constructs `SystemMonitorApp` without errors | Pass |
| Widget smoke tests | Instantiate CPU, memory, disk, network widgets | Widgets render initial layouts without raising exceptions | Pass |
| End-to-end refresh | Trigger monitor collection and widget update cycle | No unhandled exceptions; UI reflects new data | Pass |

In the final automated run, all tests in the `tests/` directory passed (`pytest tests/ -v`), confirming that these and many additional cases executed successfully.

## 7.3 Performance Evaluation

Performance evaluation focused on verifying that systop satisfies its non-functional requirements without imposing undue overhead on the host system. While exhaustive benchmarking across many hardware configurations was outside the project’s scope, a combination of automated checks and manual observation provided meaningful evidence of performance characteristics.

The automated test suite itself executes quickly: running `pytest tests/ -v` completes in under five seconds on a typical development machine, indicating that unit and integration tests remain lightweight. More importantly, interactive runs of `python main.py` showed that the application starts promptly and that the interface remains responsive under normal conditions.

Resource usage was evaluated informally using standard Linux tools such as `top` and `ps`. During idle monitoring on a development workstation, systop’s own CPU usage remained within the target band specified in the requirements (generally below a few percent), and memory consumption stabilized well within the 100 MB guideline. These observations reflect the benefits of using fixed-size circular buffers for historical data, as well as the decision to sample slow-changing metrics (such as disk and sensors) less frequently than fast-changing ones (CPU, memory, network).

Longer-running stability tests, as outlined in the final testing checklist, are designed to confirm that memory usage does not grow unbounded over a thirty-minute session and that the application remains responsive under intermittent user interaction. The architectural safeguards—bounded buffers, centralized configuration of update intervals, and conservative sampling—provide a strong basis for meeting these goals, and early exploratory runs have not revealed evidence of leaks or runaway resource consumption.

## 7.4 Comparison with Existing Tools

A qualitative comparison with established system monitoring tools helps contextualize systop’s capabilities and trade-offs. Traditional tools like `top` and `htop` are highly efficient and widely available but provide limited historical visualization and less structured integration across metrics. Graphical tools such as GNOME System Monitor and KSysGuard offer rich visualizations but require a graphical environment and are less convenient over remote connections.

Systop occupies a middle ground closer to tools like `glances` and `btop++`. Like `glances`, it provides a broad view of system metrics within a single interface, but systop emphasizes a clear separation between data collection and presentation and a strong testing story. Compared to `btop++`, systop trades some graphical sophistication and absolute performance for the flexibility and rapid development afforded by Python and Textual.

From a feature standpoint, systop aligns well with the capabilities of these modern monitors: it offers per-core CPU graphs, memory and swap visualization, disk and network graphs, basic GPU and sensor reporting where available, and an interactive process table with search and pagination. Its modular architecture and extensive tests are particular strengths when considered from a software engineering perspective, even if its raw efficiency cannot fully match highly optimized C or C++ implementations.

## 7.5 Execution Results and Screenshots

Execution results provide tangible evidence that systop behaves as designed. The final testing report documents that all automated tests pass, that core monitoring widgets display and update correctly, and that GPU and sensor unavailability are handled gracefully. Manual test notes confirm that the application starts cleanly, that metrics update in real time, and that key visual elements—graphs, progress bars, and tables—render as expected.

In a complete thesis or project report, this section would typically include annotated screenshots demonstrating key views of the application in operation. For systop, representative screenshots might include:

- The main dashboard view, showing CPU, memory, disk, and network widgets updating simultaneously.
- A close-up of the CPU widget, highlighting per-core utilization and the history graph.
- The process management view, with the process table visible, a search query active, and pagination controls in use.
- An example of graceful degradation, such as the GPU widget displaying "N/A" on a system without a compatible GPU.

These images can be captured directly from a running instance of `python main.py` using standard screenshot tools and embedded into the final document as figures, with captions referencing the behaviors described in the preceding sections. Together with the quantitative and qualitative evidence provided by the tests, they complete the picture of systop as a reliable, well-engineered system monitoring tool.
