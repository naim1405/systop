"""Disk widget for displaying disk usage and I/O metrics in the TUI.

This module provides the DiskWidget class that visualizes disk partition usage
and I/O rates with ASCII graphs and statistics.
"""

from typing import Optional, Dict, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
import plotext as plt

from src.monitors.disk import DiskMonitor
from src.utils.formatters import format_bytes, format_percentage, format_speed


class DiskWidget(Widget):
    """Widget for displaying disk information and graphs.
    
    Displays real-time disk metrics including:
    - List of disk partitions with usage bars
    - Partition usage statistics (used/total, percentage)
    - Disk I/O rates (read/write speeds)
    - ASCII graph of I/O rates over time
    
    Attributes:
        data: Reactive property storing current disk metrics
        monitor: DiskMonitor instance for data collection
        
    Example:
        disk_monitor = DiskMonitor()
        disk_widget = DiskWidget(disk_monitor)
    """
    
    data: Optional[Dict[str, Any]] = reactive(None)
    
    def __init__(self, monitor: DiskMonitor, **kwargs):
        """Initialize disk widget with a monitor.
        
        Args:
            monitor: DiskMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        self.set_interval(5.0, self.refresh_data)  # 5-second interval
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        self.data = self.monitor.collect()
        
    def _create_graph(self) -> str:
        """Create ASCII graph of I/O rates over time using plotext.
        
        Returns:
            String containing the ASCII graph
        """
        history = self.monitor.get_history()
        
        if not history or len(history) == 0:
            return "No data available"
        
        # Configure plotext for ASCII output
        plt.clf()  # Clear previous plot
        plt.theme('clear')  # Use clear theme for better compatibility
        
        # X-axis: negative numbers counting back from 0 (most recent)
        x_data = list(range(-len(history) + 1, 1))
        
        # Plot the data with color
        plt.plot(x_data, history, marker='braille', color='magenta')
        
        # Configure plot appearance
        plt.title("Total I/O Rate Over Time")
        plt.xlabel("Intervals Ago (5s)")
        plt.ylabel("B/s")
        
        # Set a larger plot size for better visibility
        plt.plotsize(100, 10)
        
        # Build the plot and return as string
        return plt.build()
    
    def _create_partition_table(self) -> Table:
        """Create a table with partition usage information.
        
        Returns:
            Rich Table with partition information and usage bars
        """
        table = Table(show_header=True, box=None, padding=(0, 1))
        table.add_column("Device", style="magenta", no_wrap=True)
        table.add_column("Mountpoint", style="white", no_wrap=True)
        table.add_column("Used / Total", style="white")
        table.add_column("Usage", style="white")
        
        if not self.data or not self.data['partitions']:
            table.add_row("No data", "-", "-", "-")
            return table
        
        for partition in self.data['partitions']:
            device = partition['device']
            mountpoint = partition['mountpoint']
            used = format_bytes(partition['used'])
            total = format_bytes(partition['total'])
            percent = partition['percent']
            
            # Create a simple text-based progress bar
            bar_width = 20
            filled = int((percent / 100.0) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Color based on usage
            if percent < 70:
                bar_color = "green"
            elif percent < 90:
                bar_color = "yellow"
            else:
                bar_color = "red"
            
            usage_str = f"[{bar_color}]{bar}[/{bar_color}] {format_percentage(percent)}"
            
            table.add_row(
                device,
                mountpoint,
                f"{used} / {total}",
                usage_str
            )
        
        return table
    
    def _create_io_stats(self) -> Table:
        """Create a table with I/O statistics.
        
        Returns:
            Rich Table with I/O rate information
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="magenta", no_wrap=True)
        table.add_column("Value", style="white")
        
        if not self.data:
            table.add_row("Status", "Loading...")
            return table
        
        io = self.data['io']
        
        # Read speed
        read_speed = format_speed(io['read_bytes_per_sec'])
        table.add_row("Read Speed", read_speed)
        
        # Write speed
        write_speed = format_speed(io['write_bytes_per_sec'])
        table.add_row("Write Speed", write_speed)
        
        # Total operations
        table.add_row("Read Operations", f"{io['read_count']:,}")
        table.add_row("Write Operations", f"{io['write_count']:,}")
        
        return table
    
    def render(self) -> RenderableType:
        """Render the disk widget with partitions, I/O stats, and graph.
        
        Returns:
            Rich Panel containing disk information
        """
        if not self.data:
            return Panel(
                Text("Loading disk data...", style="italic dim"),
                title="[bold magenta]Disk[/bold magenta]",
                border_style="magenta"
            )
        
        # Create partitions table
        partition_table = self._create_partition_table()
        
        # Create I/O stats table
        io_stats = self._create_io_stats()
        
        # Create the graph
        graph_str = self._create_graph()
        
        # Combine all elements
        from rich.console import Group
        content = Group(
            Text("[bold]Partitions:[/bold]"),
            partition_table,
            Text(""),  # Empty line for spacing
            Text("[bold]I/O Statistics:[/bold]"),
            io_stats,
            Text(""),  # Empty line for spacing
            Text(graph_str)
        )
        
        # Calculate total I/O for dynamic title
        total_io = self.data['io']['read_bytes_per_sec'] + self.data['io']['write_bytes_per_sec']
        total_io_str = format_speed(total_io)
        title = f"[bold]Disk[/bold] - {total_io_str}"
        
        # Dynamic border color based on I/O activity
        if total_io < 1_000_000:  # < 1 MB/s
            border_color = "magenta"
        elif total_io < 10_000_000:  # < 10 MB/s
            border_color = "blue"
        elif total_io < 50_000_000:  # < 50 MB/s
            border_color = "yellow"
        else:
            border_color = "red"
        
        return Panel(
            content,
            title=title,
            border_style=border_color
        )
