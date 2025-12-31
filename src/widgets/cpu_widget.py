"""CPU widget for displaying CPU metrics in the TUI.

This module provides the CPUWidget class that visualizes CPU usage,
frequency, load averages, and per-core statistics with ASCII graphs.
"""

from typing import Optional, Dict, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import plotext as plt

from src.monitors.cpu import CPUMonitor
from src.utils.formatters import format_percentage, format_frequency


class CPUWidget(Widget):
    """Widget for displaying CPU information and graphs.
    
    Displays real-time CPU metrics including:
    - ASCII graph of overall CPU usage over time
    - Per-core CPU usage percentages
    - CPU frequency information
    - System load averages
    - CPU model name
    
    Attributes:
        data: Reactive property storing current CPU metrics
        monitor: CPUMonitor instance for data collection
        
    Example:
        cpu_monitor = CPUMonitor()
        cpu_widget = CPUWidget(cpu_monitor)
    """
    
    data: Optional[Dict[str, Any]] = reactive(None)
    
    def __init__(self, monitor: CPUMonitor, **kwargs):
        """Initialize CPU widget with a monitor.
        
        Args:
            monitor: CPUMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        self.set_interval(1.0, self.refresh_data)
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        self.data = self.monitor.collect()
        
    def _create_graph(self) -> str:
        """Create ASCII graph of CPU usage over time using plotext.
        
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
        plt.plot(x_data, history, marker='braille', color='cyan')
        
        # Configure plot appearance
        plt.title("CPU Usage Over Time")
        plt.xlabel("Seconds Ago")
        plt.ylabel("%")
        plt.ylim(0, 100)
        
        # Set a larger plot size for better visibility
        plt.plotsize(100, 12)
        
        # Build the plot and return as string
        return plt.build()
    
    def _create_stats_table(self) -> Table:
        """Create a table with CPU statistics.
        
        Returns:
            Rich Table with CPU information
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if not self.data:
            table.add_row("Status", "Loading...")
            return table
        
        # CPU Model
        table.add_row("Model", self.data['model'])
        
        # Overall usage
        overall = format_percentage(self.data['overall_percent'])
        table.add_row("Overall Usage", overall)
        
        # Per-core usage - show in a compact format
        per_core = self.data['per_core_percent']
        if per_core:
            # Format cores in groups of 4 for readability
            core_groups = []
            for i in range(0, len(per_core), 4):
                group = per_core[i:i+4]
                formatted = [format_percentage(usage, precision=1) for usage in group]
                core_groups.append("  ".join(f"C{i+j}:{val}" for j, val in enumerate(formatted)))
            
            table.add_row("Per-Core", core_groups[0] if core_groups else "N/A")
            for group in core_groups[1:]:
                table.add_row("", group)
        
        # Frequency
        freq = self.data['frequency']
        freq_str = f"{format_frequency(freq['current'])} (min: {format_frequency(freq['min'])}, max: {format_frequency(freq['max'])})"
        table.add_row("Frequency", freq_str)
        
        # Core counts
        counts = self.data['cpu_count']
        cores_str = f"Physical: {counts['physical']}, Logical: {counts['logical']}"
        table.add_row("Cores", cores_str)
        
        # Load averages
        load = self.data['load_avg']
        load_str = f"1m: {load['1min']:.2f}, 5m: {load['5min']:.2f}, 15m: {load['15min']:.2f}"
        table.add_row("Load Average", load_str)
        
        return table
    
    def render(self) -> RenderableType:
        """Render the CPU widget with graph and statistics.
        
        Returns:
            Rich Panel containing CPU information
        """
        if not self.data:
            return Panel(
                Text("Loading CPU data...", style="italic dim"),
                title="[bold cyan]CPU[/bold cyan]",
                border_style="cyan"
            )
        
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
        
        # Get overall usage for dynamic title and border color
        overall = self.data['overall_percent']
        title = f"[bold]CPU[/bold] - {format_percentage(overall)}"
        
        # Dynamic border color based on usage
        if overall < 50:
            border_color = "cyan"
        elif overall < 80:
            border_color = "blue"
        elif overall < 95:
            border_color = "yellow"
        else:
            border_color = "red"
        
        return Panel(
            content,
            title=title,
            border_style=border_color
        )
