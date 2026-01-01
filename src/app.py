#!/usr/bin/env python3
"""Main Textual application for systop system monitor"""

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer

from src.monitors.cpu import CPUMonitor
from src.monitors.memory import MemoryMonitor
from src.monitors.disk import DiskMonitor
from src.monitors.network import NetworkMonitor
from src.monitors.gpu import GPUMonitor
from src.monitors.sensors import SensorsMonitor
from src.monitors.processes import ProcessMonitor
from src.widgets.cpu_widget import CPUWidget
from src.widgets.memory_widget import MemoryWidget
from src.widgets.disk_widget import DiskWidget
from src.widgets.network_widget import NetworkWidget
from src.widgets.gpu_widget import GPUWidget
from src.widgets.sensors_widget import SensorsWidget
from src.widgets.process_widget import ProcessWidget


class SystemMonitorApp(App):
    """A btop-like system monitor TUI application
    
    Provides real-time monitoring of system resources including:
    - CPU usage, frequency, and per-core statistics
    - Memory and swap usage
    - Disk I/O and usage
    - Network bandwidth
    - GPU metrics (if available)
    - Temperature sensors
    - Process management with sorting, filtering, and kill capabilities
    
    Keyboard Bindings:
        q: Quit application
        r: Force refresh all widgets
        (Process-specific keys work when process widget is focused)
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_all", "Refresh"),
    ]
    
    def __init__(self, **kwargs):
        """Initialize the app with monitors."""
        super().__init__(**kwargs)
        # Initialize monitors
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.network_monitor = NetworkMonitor()
        self.gpu_monitor = GPUMonitor()
        self.sensors_monitor = SensorsMonitor()
        self.process_monitor = ProcessMonitor()
        
        # Track widget references for cleanup
        self._widgets = []
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    VerticalScroll {
        height: 100%;
        background: $surface;
        scrollbar-background: $panel;
        scrollbar-color: $primary;
    }
    
    Container {
        height: auto;
        margin: 1 0;
        padding: 0;
        background: transparent;
    }
    
    #cpu_container {
        min-height: 10;
    }
    
    #memory_container {
        min-height: 8;
    }
    
    #disk_container {
        min-height: 8;
    }
    
    #network_container {
        min-height: 8;
    }
    
    #gpu_container {
        min-height: 8;
    }
    
    #sensors_container {
        min-height: 6;
    }
    
    #process_container {
        min-height: 15;
    }
    
    /* Focused widget border highlight */
    Widget:focus {
        border: heavy $accent;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Build UI structure with widgets"""
        yield Header(show_clock=True)
        with VerticalScroll():
            cpu_widget = CPUWidget(self.cpu_monitor, id="cpu_container")
            memory_widget = MemoryWidget(self.memory_monitor, id="memory_container")
            disk_widget = DiskWidget(self.disk_monitor, id="disk_container")
            network_widget = NetworkWidget(self.network_monitor, id="network_container")
            gpu_widget = GPUWidget(self.gpu_monitor, id="gpu_container")
            sensors_widget = SensorsWidget(self.sensors_monitor, id="sensors_container")
            process_widget = ProcessWidget(self.process_monitor, id="process_container")
            
            # Track widgets for cleanup
            self._widgets = [
                cpu_widget, memory_widget, disk_widget, network_widget,
                gpu_widget, sensors_widget, process_widget
            ]
            
            yield cpu_widget
            yield memory_widget
            yield disk_widget
            yield network_widget
            yield gpu_widget
            yield sensors_widget
            yield process_widget
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup after UI is mounted"""
        # Give focus to process widget for keyboard navigation
        try:
            process_widget = self.query_one(ProcessWidget)
            process_widget.focus()
        except Exception:
            pass  # Silently fail if process widget not found
    
    def on_unmount(self) -> None:
        """Cleanup when app is shutting down"""
        # Stop all widget timers gracefully
        for widget in self._widgets:
            try:
                # Widgets use set_interval which Textual handles automatically
                # but we can add explicit cleanup if needed
                pass
            except Exception:
                pass  # Ignore cleanup errors
    
    def action_quit(self) -> None:
        """Quit application gracefully"""
        self.exit()
    
    def action_refresh_all(self) -> None:
        """Force refresh all widgets immediately"""
        for widget in self._widgets:
            try:
                if hasattr(widget, 'refresh_data'):
                    widget.refresh_data()
            except Exception as e:
                # Log error but don't crash the app
                self.log(f"Error refreshing widget {widget.__class__.__name__}: {e}")


def main():
    """Entry point for systop application"""
    app = SystemMonitorApp()
    try:
        app.run()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
