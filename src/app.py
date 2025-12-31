#!/usr/bin/env python3
"""Main Textual application for systop system monitor"""

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer


class SystemMonitorApp(App):
    """A btop-like system monitor TUI application"""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    
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
        """Build UI structure with empty containers"""
        yield Header(show_clock=True)
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
        """Setup after UI is mounted"""
        # Set border titles
        self.query_one("#cpu_container", Container).border_title = "CPU"
        self.query_one("#memory_container", Container).border_title = "Memory"
        self.query_one("#disk_container", Container).border_title = "Disk"
        self.query_one("#network_container", Container).border_title = "Network"
        self.query_one("#gpu_container", Container).border_title = "GPU"
        self.query_one("#sensors_container", Container).border_title = "Sensors"
        self.query_one("#process_container", Container).border_title = "Processes"
        # Empty for now - will add timers later
    
    def action_quit(self) -> None:
        """Quit application"""
        self.exit()


def main():
    """Entry point for systop application"""
    app = SystemMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
