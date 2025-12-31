"""Network widget for displaying bandwidth and traffic metrics in the TUI.

This module provides the NetworkWidget class that visualizes network bandwidth
rates and statistics with ASCII graphs.
"""

from typing import Optional, Dict, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import plotext as plt

from src.monitors.network import NetworkMonitor
from src.utils.formatters import format_bytes, format_speed


class NetworkWidget(Widget):
    """Widget for displaying network information and graphs.
    
    Displays real-time network metrics including:
    - Upload and download speeds (bandwidth rates)
    - Total data transferred (sent/received)
    - Packet counts
    - ASCII graphs of bandwidth over time
    
    Attributes:
        data: Reactive property storing current network metrics
        monitor: NetworkMonitor instance for data collection
        
    Example:
        network_monitor = NetworkMonitor()
        network_widget = NetworkWidget(network_monitor)
    """
    
    data: Optional[Dict[str, Any]] = reactive(None)
    
    def __init__(self, monitor: NetworkMonitor, **kwargs):
        """Initialize network widget with a monitor.
        
        Args:
            monitor: NetworkMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        self.set_interval(1.0, self.refresh_data)  # 1-second interval
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        self.data = self.monitor.collect()
        
    def _create_graph(self) -> str:
        """Create ASCII graph of bandwidth over time using plotext.
        
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
        plt.plot(x_data, history, marker='braille', color='cyan')
        
        # Configure plot appearance
        plt.title("Total Bandwidth Over Time")
        plt.xlabel("Seconds Ago")
        plt.ylabel("B/s")
        
        # Set a larger plot size for better visibility
        plt.plotsize(100, 10)
        
        # Build the plot and return as string
        return plt.build()
    
    def _create_bandwidth_stats(self) -> Table:
        """Create a table with bandwidth statistics.
        
        Returns:
            Rich Table with bandwidth rate information
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if not self.data:
            table.add_row("Status", "Loading...")
            return table
        
        # Upload speed
        upload_speed = format_speed(self.data['bytes_sent_per_sec'])
        table.add_row("↑ Upload Speed", upload_speed)
        
        # Download speed
        download_speed = format_speed(self.data['bytes_recv_per_sec'])
        table.add_row("↓ Download Speed", download_speed)
        
        # Total bandwidth
        total_bandwidth = self.data['bytes_sent_per_sec'] + self.data['bytes_recv_per_sec']
        total_bandwidth_str = format_speed(total_bandwidth)
        table.add_row("Total Bandwidth", total_bandwidth_str)
        
        return table
    
    def _create_traffic_stats(self) -> Table:
        """Create a table with cumulative traffic statistics.
        
        Returns:
            Rich Table with cumulative data and packet counts
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if not self.data:
            table.add_row("Status", "Loading...")
            return table
        
        # Total sent
        total_sent = format_bytes(self.data['total_sent'])
        table.add_row("Total Sent", total_sent)
        
        # Total received
        total_recv = format_bytes(self.data['total_recv'])
        table.add_row("Total Received", total_recv)
        
        # Packets sent
        table.add_row("Packets Sent", f"{self.data['packets_sent']:,}")
        
        # Packets received
        table.add_row("Packets Received", f"{self.data['packets_recv']:,}")
        
        return table
    
    def render(self) -> RenderableType:
        """Render the network widget with bandwidth, traffic stats, and graph.
        
        Returns:
            Rich Panel containing network information
        """
        if not self.data:
            return Panel(
                Text("Loading network data...", style="italic dim"),
                title="[bold cyan]Network[/bold cyan]",
                border_style="cyan"
            )
        
        # Create bandwidth stats table
        bandwidth_stats = self._create_bandwidth_stats()
        
        # Create traffic stats table
        traffic_stats = self._create_traffic_stats()
        
        # Create the graph
        graph_str = self._create_graph()
        
        # Combine all elements
        from rich.console import Group
        content = Group(
            Text.from_markup("[bold]Bandwidth:[/bold]"),
            bandwidth_stats,
            Text(""),  # Empty line for spacing
            Text.from_markup("[bold]Traffic Statistics:[/bold]"),
            traffic_stats,
            Text(""),  # Empty line for spacing
            Text(graph_str)
        )
        
        # Calculate total bandwidth for dynamic title
        total_bandwidth = self.data['bytes_sent_per_sec'] + self.data['bytes_recv_per_sec']
        bandwidth_str = format_speed(total_bandwidth)
        title = f"Network - {bandwidth_str}"
        
        # Dynamic border color based on bandwidth activity
        if total_bandwidth < 100_000:  # < 100 KB/s
            border_color = "cyan"
        elif total_bandwidth < 1_000_000:  # < 1 MB/s
            border_color = "blue"
        elif total_bandwidth < 10_000_000:  # < 10 MB/s
            border_color = "yellow"
        else:
            border_color = "red"
        
        return Panel(
            content,
            title=title,
            border_style=border_color
        )
