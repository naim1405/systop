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
from src.widgets.cpu_widget import CPUWidget
from src.widgets.memory_widget import MemoryWidget
from src.widgets.disk_widget import DiskWidget
from src.widgets.network_widget import NetworkWidget
from src.widgets.gpu_widget import GPUWidget


class SystemMonitorApp(App):
    """A btop-like system monitor TUI application"""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
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
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    VerticalScroll {
        height: 100%;
        background: $surface;
    }
    
    Container {
        height: auto;
        border: solid $primary;
        margin: 1;
        padding: 1;
        background: $panel;
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
    """
    
    def compose(self) -> ComposeResult:
        """Build UI structure with widgets"""
        yield Header(show_clock=True)
        with VerticalScroll():
            yield CPUWidget(self.cpu_monitor, id="cpu_container")
            yield MemoryWidget(self.memory_monitor, id="memory_container")
            yield DiskWidget(self.disk_monitor, id="disk_container")
            yield NetworkWidget(self.network_monitor, id="network_container")
            yield GPUWidget(self.gpu_monitor, id="gpu_container")
            yield Container(id="sensors_container")
            yield Container(id="process_container")
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup after UI is mounted"""
        # Set border titles for remaining empty containers
        self.query_one("#sensors_container", Container).border_title = "Sensors"
        self.query_one("#process_container", Container).border_title = "Processes"
    
    def action_quit(self) -> None:
        """Quit application"""
        self.exit()


def main():
    """Entry point for systop application"""
    app = SystemMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
