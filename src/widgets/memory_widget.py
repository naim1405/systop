"""Memory widget for displaying memory metrics in the TUI.

This module provides the MemoryWidget class that visualizes RAM and swap usage
with ASCII graphs and statistics.
"""

from typing import Optional, Dict, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import plotext as plt

from src.monitors.memory import MemoryMonitor
from src.utils.formatters import format_bytes, format_percentage


class MemoryWidget(Widget):
    """Widget for displaying memory information and graphs.
    
    Displays real-time memory metrics including:
    - ASCII graph of RAM usage over time
    - RAM usage statistics (used/total, percentage)
    - Swap usage statistics (used/total, percentage)
    
    Attributes:
        data: Reactive property storing current memory metrics
        monitor: MemoryMonitor instance for data collection
        
    Example:
        memory_monitor = MemoryMonitor()
        memory_widget = MemoryWidget(memory_monitor)
    """
    
    data: Optional[Dict[str, Any]] = reactive(None)
    
    def __init__(self, monitor: MemoryMonitor, **kwargs):
        """Initialize memory widget with a monitor.
        
        Args:
            monitor: MemoryMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        self.set_interval(1.0, self.refresh_data)
        # Initial data fetch
        self.refresh_data()
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        try:
            self.data = self.monitor.collect()
        except Exception as e:
            self.data = {'error': str(e)}
        
    def _create_graph(self) -> str:
        """Create ASCII graph of RAM usage over time using plotext.
        
        Returns:
            String containing the ASCII graph
        """
        history = self.monitor.get_history()
        
        if not history or len(history) == 0:
            return "No data available"
        
        # Configure plotext for ASCII output
        plt.clf()  # Clear previous plot
        plt.theme('clear')  # Use clear theme for better compatibility
        
        # Reverse history so newest is on the right
        # X-axis: negative numbers counting back from 0 (most recent)
        x_data = list(range(-len(history) + 1, 1))
        
        # Plot the data with color
        plt.plot(x_data, history, marker='braille', color='green')
        
        # Configure plot appearance
        plt.title("RAM Usage Over Time")
        plt.xlabel("Seconds Ago")
        plt.ylabel("%")
        plt.ylim(0, 100)
        
        # Set a larger plot size for better visibility
        plt.plotsize(100, 12)
        
        # Build the plot and return as string
        return plt.build()
    
    def _create_stats_table(self) -> Table:
        """Create a table with memory statistics.
        
        Returns:
            Rich Table with memory information
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        
        if not self.data:
            table.add_row("Status", "Loading...")
            return table
        
        # RAM statistics
        ram = self.data['ram']
        ram_used_str = f"{format_bytes(ram['used'])} / {format_bytes(ram['total'])}"
        ram_percent_str = format_percentage(ram['percent'])
        table.add_row("RAM Used", f"{ram_used_str} ({ram_percent_str})")
        
        ram_available_str = format_bytes(ram['available'])
        table.add_row("RAM Available", ram_available_str)
        
        # Swap statistics
        swap = self.data['swap']
        if swap['total'] > 0:
            swap_used_str = f"{format_bytes(swap['used'])} / {format_bytes(swap['total'])}"
            swap_percent_str = format_percentage(swap['percent'])
            table.add_row("Swap Used", f"{swap_used_str} ({swap_percent_str})")
        else:
            table.add_row("Swap Used", "No swap configured")
        
        return table
    
    def render(self) -> RenderableType:
        """Render the memory widget with graph and statistics.
        
        Returns:
            Rich Panel containing memory information
        """
        # Handle error state
        if self.data and 'error' in self.data:
            return Panel(
                Text(f"Error: {self.data['error']}", style="red"),
                title="[bold red]Memory - Error[/bold red]",
                border_style="red"
            )
        
        if not self.data:
            return Panel(
                Text("Loading memory data...", style="italic dim"),
                title="[bold green]Memory[/bold green]",
                border_style="green"
            )
        
        try:
            # Create the graph
            graph_str = self._create_graph()
            
            # Create the stats table
            stats_table = self._create_stats_table()
            
            # Combine graph and table
            from rich.console import Group
            content = Group(
                Text(graph_str),
                Text(""),  # Empty line for spacing
                stats_table
            )
            
            # Get RAM usage for dynamic title and border color
            ram_percent = self.data['ram']['percent']
            title = f"[bold]Memory[/bold] - {format_percentage(ram_percent)}"
            
            # Dynamic border color based on usage
            if ram_percent < 50:
                border_color = "green"
            elif ram_percent < 80:
                border_color = "blue"
            elif ram_percent < 95:
                border_color = "yellow"
            else:
                border_color = "red"
            
            return Panel(
                content,
                title=title,
                border_style=border_color
            )
        except Exception as e:
            return Panel(
                Text(f"Render error: {str(e)}", style="red"),
                title="[bold red]Memory - Error[/bold red]",
                border_style="red"
            )
