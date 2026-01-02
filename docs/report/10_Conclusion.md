# Chapter 10: Conclusion

This chapter concludes the systop project by summarizing the work accomplished, assessing the degree to which the original objectives have been achieved, and reflecting on the overall significance and value of the system. Taken together, the preceding chapters document the journey from initial problem statement through design, implementation, testing, and reflection, positioning systop as both a practical tool and a learning vehicle.

## 10.1 Summary of Work

The project began with the recognition that existing system monitoring tools, while powerful, often require users to juggle multiple interfaces or accept limited historical visualization and process management features. In response, systop set out to provide a unified, interactive terminal-based monitoring application for Linux that consolidates CPU, memory, disk, network, GPU, sensor, and process metrics into a single, coherent view.

To realize this vision, the work was structured around a clear build plan and a layered architecture. Core utility modules were implemented to handle history management and value formatting, followed by a centralized configuration system and an abstract base monitor class. Concrete monitors for each subsystem were then developed, encapsulating the logic required to collect and interpret system metrics. Widgets built with Textual transformed these metrics into a responsive TUI, and the `SystemMonitorApp` coordinated data collection, user input, and layout.

Throughout development, the project maintained a strong emphasis on testing, documentation, and maintainability. Unit and integration tests were written alongside features, and the final automated test run reported full success across more than a hundred tests with high coverage of critical modules. Documentation in the form of build plans, prompts, and this report captured the rationale for key decisions and provided guidance for future contributors or extensions.

The result is a functioning system monitor that can be launched on a Linux machine to provide real-time insight into system behavior, complemented by a well-organized codebase and a comprehensive narrative of its development.

## 10.2 Achievement of Objectives

The objectives defined in the introduction provide a useful lens for evaluating the project’s success.

The first objective was to develop a comprehensive monitoring solution. Systop achieves this by supporting real-time monitoring of CPU (including per-core usage and load averages), memory and swap, disk utilization and I/O, network bandwidth, GPU status where available, and temperature sensors when supported by the hardware. Historical graphs and trend information are provided for key metrics such as CPU, memory, disk, and network, giving users more context than instantaneous values alone.

The second objective focused on creating an intuitive user interface. The Textual-based TUI delivers a structured layout with clearly delineated sections for each subsystem, a header and footer for orientation and keybindings, and interactive elements such as scrollable views and process tables. Visual consistency is maintained across widgets, and the use of ASCII graphs and progress bars provides at-a-glance understanding of system state.

The third objective was to enable interactive process management. The process widget presents a detailed, paginated list of running processes with CPU and memory usage, supports sorting and searching, and provides a controlled mechanism for terminating processes with appropriate confirmation and error handling. While some aspects of interactive testing remain candidates for further refinement, the implemented features meet the functional requirements laid out at the start of the project.

The fourth objective concerned reliability, cross-hardware behavior, and performance. Systop targets Linux explicitly and handles hardware variability—particularly around GPUs and sensors—through graceful degradation. Performance observations indicate that the application operates within the CPU and memory bounds specified, aided by bounded history buffers and sensible update intervals. Automated tests and manual exploration together support the conclusion that the system is stable under typical usage conditions.

The fifth objective was to follow sound software engineering practices. The modular architecture, comprehensive tests, consistent coding style, and detailed documentation collectively demonstrate adherence to these principles. The project’s structure makes it straightforward to extend or modify, and the presence of a clear build plan and test suite encourages further evolution without sacrificing quality.

Taken as a whole, the project substantially meets the objectives originally set, delivering both a working application and a high-quality code and documentation base.

## 10.3 Final Remarks

Systop represents a meaningful contribution at several levels. Practically, it offers Linux users a modern, extensible, and well-tested system monitoring tool that delivers rich information in a compact terminal interface. For developers and students, it serves as a detailed case study in designing, implementing, and validating a non-trivial application using contemporary Python tools and frameworks.

The project also demonstrates the value of a disciplined, incremental approach to software development. By decomposing the work into manageable steps, maintaining a strong testing culture, and documenting decisions along the way, it was possible to move from concept to implementation without losing sight of overall goals. The resulting system is not perfect—no system is—but it is coherent, robust, and open to future enhancement.

Ultimately, the significance of systop lies not only in the specific features it offers today but in the foundation it provides for future work. Whether extended to support additional platforms, integrated into larger monitoring solutions, or used as inspiration for new tools, the ideas and patterns developed here will remain valuable. In that sense, the conclusion of this project is also the starting point for further exploration and growth.
