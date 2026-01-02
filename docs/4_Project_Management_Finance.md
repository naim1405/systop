# Chapter 4: Project Management & Finance

This chapter presents the management and financial perspective of the systop project. It explains how the work was structured, how the schedule evolved over the life of the project, how effort and cost were managed, and how risks and key decisions were handled. While the technical chapters focus on what was built, this chapter focuses on how it was built and governed.

## 4.1 Work Breakdown Structure (WBS)

The systop project was organized around a hierarchical Work Breakdown Structure that mapped directly onto the 16-step build plan. This structure provided a clear view from high-level phases down to concrete implementation tasks, ensuring that no essential activity was overlooked and that progress could be tracked meaningfully.

At the highest level, the project was divided into several phases. The initiation and planning phase captured the problem statement, objectives, constraints, and success criteria. During this phase, the overall vision of a btop-like system monitor was translated into concrete requirements, and the technology stack—Python, Textual, psutil, and the supporting libraries—was selected. Key project documents such as BUILD_PLAN.md and AGENT_PROMPTS.md were produced here, forming the backbone for subsequent work.

The architecture and design phase established the core structure of the system. The application was conceptually divided into monitors, widgets, an application controller, and a utilities layer. Data flow between these components, as well as update intervals and configuration mechanisms, were defined. The testing strategy was also outlined at this stage, setting expectations for unit tests, integration tests, and stability tests that would accompany each major increment.

The core infrastructure implementation phase focused on the foundation of the codebase: creating the project scaffolding, establishing the virtual environment, implementing the utility modules for history and formatting, and introducing the centralized configuration system. The abstract base monitor class and the base Textual application canvas were created here, providing a solid platform upon which all later functionality would rest.

Subsequent phases concentrated on the monitoring modules themselves. Each major subsystem—CPU, memory, disk, network, processes, GPU, and sensors—was implemented as a dedicated monitor and paired widget. These were not treated as isolated pieces of work; each module brought with it its own logic, tests, and integration points. Once the monitors were in place, an integration and interaction phase refined the connections between them, added global keybindings, and delivered the interactive process management workflow, including search, pagination, and safe process termination.

The final phases addressed testing, validation, refinement, documentation, and release. Automated tests were expanded, edge cases were explored and handled, and long-running stability checks were performed. Parallel to this, user-facing and technical documentation were written, and the final report—including this chapter—was assembled.

At a more detailed level, the 16 steps of the build plan served as Level 2 of the WBS. Each step corresponded to a tangible increment—such as “utilities,” “configuration,” “CPU module,” or “process interactions”—with its own definition of done. This fine-grained structure ensured that each commit and development session could be associated with a clearly articulated objective.

## 4.2 Project Schedule

Rather than anchoring the schedule to strict calendar dates, the project adopted a phase-based schedule aligned with the WBS. This approach is particularly suitable for a solo developer environment, where flexibility and the ability to adapt to new insights are more valuable than rigid deadlines.

The early part of the schedule was dedicated to planning and setup. Within approximately a day, the repository structure, virtual environment, dependency definitions, and basic configuration files were established. This front-loaded effort ensured that later work could proceed without repeated setup friction.

The next several days were spent on core infrastructure. During this period, the utility modules were implemented and tested, the configuration system was introduced, and the base monitor abstraction and Textual application shell were created. This phase culminated in a running but minimal application—essentially an empty canvas capable of rendering containers and responding to basic input.

The bulk of the project time was allocated to developing the monitoring modules and their widgets. Over roughly one to two weeks of focused effort, each subsystem was implemented in turn, starting with CPU and memory and extending through disk, network, processes, GPU, and sensors. Each new module followed a consistent pattern: design the monitor, implement the widget, wire it into the application, and write supporting tests. This incrementalism allowed the schedule to adapt to the complexity of individual modules; for example, the process module received additional attention due to its interactive nature.

Integration and interaction refinements formed the next phase. During this time, timers were tuned, process management workflows were finalized, and cross-cutting behaviors such as error handling and fallback behaviors were harmonized across widgets. The scheduling of this phase reflected its dependency on the preceding work: it could only begin once each component existed and had a baseline of tests.

The final days of the schedule were devoted to testing, stabilization, and documentation. The full test suite was run continuously as functionality matured, and additional tests were added to cover previously untested paths. Manual exploratory testing, particularly under different system loads and hardware configurations, complemented automated checks. In parallel, documentation—including the chapters of this report—was drafted and revised.

Across all phases, the critical path of the project ran from environment setup through utilities, configuration, monitors, widgets, integration, testing, and documentation. Many activities (such as documentation drafting or minor refactors) could be interleaved or parallelized with core development work, but no major step skipped ahead of its dependencies. This disciplined ordering reduced the likelihood of rework and ensured that the project progressed in a controlled, predictable manner.

## 4.3 Budget and Financial Cost Analysis

The financial profile of systop is shaped primarily by its reliance on open-source tools and a single-developer effort model. No licenses, hosting arrangements, or third-party services were purchased to complete the project. All libraries—Textual, psutil, plotext, py-cpuinfo, GPUtil, pytest—are freely available under permissive licenses, and the development environment itself (Linux, Python, VS Code, terminal tools, and Git) incurs no direct cost.

In this context, the project’s most significant resource is time. The development effort is estimated at approximately forty to sixty hours, encompassing planning, implementation, testing, and documentation. When mapped against the phases of the WBS, this effort is distributed sensibly: a modest share dedicated to up-front design and environment setup, a substantial portion focused on implementing and refining the monitors and widgets, and the remainder devoted to testing, performance tuning, and writing documentation.

From a financial planning standpoint, this effort could be expressed as an opportunity cost or converted into a monetary value using a standard hourly rate, but no actual expenditure was incurred beyond the use of existing hardware and internet access. What matters more is how that time was used. By leaning heavily on mature libraries and frameworks, the project avoided reimplementing low-level functionality such as process enumeration, CPU metric collection, or terminal rendering. This significantly reduced the time required to reach a high-quality, feature-complete system.

Cost control was achieved through a combination of strict scope management and an incremental development methodology. The decision to target Linux exclusively, to support NVIDIA GPUs rather than attempting full cross-vendor GPU coverage, and to limit persistent storage needs kept both complexity and time investment within manageable bounds. Automated tests, although requiring up-front effort, paid off by reducing debugging time and enabling safe refactoring later in the project.

## 4.4 Risk Analysis and Mitigation

Risk management for systop focused on a set of realistic challenges that could have undermined the project’s objectives: dependency volatility, performance overhead, hardware variability, schedule pressure, and test coverage gaps.

Dependency risk arises whenever a project builds on actively developed libraries. Textual and psutil, while mature and well-maintained, evolve over time, and breaking changes or deprecations can surface unexpectedly. To mitigate this, dependencies were specified with explicit minimum versions in the project configuration files, and the code relied on stable, well-documented APIs. The architecture’s modularity also helps: should a particular library require replacement in the future, the impact is confined to a relatively small part of the codebase.

Performance risk is inherent in using a high-level language and a rich TUI framework for a monitoring application. To address this, the implementation makes careful use of efficient data structures and controlled update intervals. The history of metrics is stored in fixed-size circular buffers, ensuring that memory usage remains bounded even for long-running sessions, and fast-changing metrics are sampled more frequently than slow-changing ones to balance responsiveness and overhead. Informal profiling and testing under load further helped confirm that systop behaves acceptably on typical hardware.

Hardware variability represents one of the more significant uncertainties: users may run the application on systems without GPUs, without temperature sensors, or with unusual configurations. Instead of assuming ideal hardware, systop was built around the idea of graceful degradation. GPU and sensor access are always wrapped in defensive error handling, and when a capability is unavailable, the corresponding widget clearly reports that fact instead of failing. This approach ensures that the application remains stable and useful across a broad range of environments.

Schedule risk was managed through the use of the 16-step build plan and the discipline of treating each step as a mini-project with its own deliverables. When complexity in a particular area—such as process management—proved higher than anticipated, the plan could absorb that by temporarily prioritizing the most critical aspects of the feature and postponing minor enhancements. This flexibility prevented localized delays from jeopardizing the entire project.

Finally, the risk of insufficient test coverage was proactively addressed by embedding testing into the normal development workflow. Utility modules and monitors were accompanied by dedicated unit tests, and integration tests ensured that the main application could start and exercise key paths without failure. While no test suite can be truly exhaustive, this approach materially reduced the probability of regressions and subtle runtime errors.

## 4.5 Summary of Management Decisions

Several management decisions, taken early and revisited as the project progressed, had a strong influence on the final outcome. The decision to target Linux exclusively simplified both design and testing, allowing the project to go deeper on one platform rather than spreading effort thinly across many. Similarly, the choice of Python, Textual, and psutil reflected a conscious trade-off: slightly higher runtime overhead in exchange for dramatically faster development and easier maintenance.

The adoption of a stepwise, 16-part build plan provided a concrete roadmap that guided implementation and gave structure to the Git history. Each step had a clear purpose and measurable completion criteria, turning what could have been an open-ended development process into a series of achievable milestones. This also made it easier to reason about progress and to communicate the state of the project at any point in time.

Another important decision was to embrace a modular architecture, with distinct boundaries between data collection, presentation, and orchestration. This not only improved code clarity but also made the system more robust in the face of change: improvements or bug fixes in one area could usually be made without destabilizing others. Closely related was the commitment to testing—treating tests as a mandatory part of feature work rather than an optional add-on. This mindset directly supported the project’s reliability and maintainability goals.

Finally, the project consistently favored resilience over completeness. Instead of attempting to support every conceivable hardware configuration or visual feature, it prioritized a stable, predictable experience across common Linux environments. The result is a system that delivers on its core promise—a powerful, interactive system monitor—within the time and resource constraints originally envisioned.
