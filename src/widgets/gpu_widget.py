"""GPU widget for displaying GPU metrics in the TUI.

This module provides the GPUWidget class that visualizes GPU usage,
memory, and temperature. Gracefully displays "N/A" when GPU is unavailable.
"""

from typing import Optional, List, Dict, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn
import plotext as plt

from src.monitors.gpu import GPUMonitor
from src.utils.formatters import format_bytes, format_percentage


class GPUWidget(Widget):
    """Widget for displaying GPU information and graphs.
    
    Displays real-time GPU metrics including:
    - GPU utilization percentage with bar
    - Memory usage (used/total)
    - Temperature
    - ASCII graph of GPU usage over time
    
    Shows "GPU: N/A" when no GPU is available.
    
    Attributes:
        data: Reactive property storing current GPU metrics (None if unavailable)
        monitor: GPUMonitor instance for data collection
        
    Example:
        gpu_monitor = GPUMonitor()
        gpu_widget = GPUWidget(gpu_monitor)
    """
    
    data: Optional[List[Dict[str, Any]]] = reactive(None)
    
    def __init__(self, monitor: GPUMonitor, **kwargs):
        """Initialize GPU widget with a monitor.
        
        Args:
            monitor: GPUMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        # Update every 2 seconds for GPU (less frequent than CPU)
        self.set_interval(2.0, self.refresh_data)
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        self.data = self.monitor.collect()
    
    def _create_graph(self) -> str:
        """Create ASCII graph of GPU usage over time using plotext.
        
        Returns:
            String containing the ASCII graph or message if no data
        """
        history = self.monitor.get_history()
        
        if not history or len(history) == 0:
            return "No data available"
        
        # Configure plotext for ASCII output
        plt.clf()  # Clear previous plot
        plt.theme('clear')
        
        # X-axis: negative numbers counting back from 0 (most recent)
        x_data = list(range(-len(history) + 1, 1))
        
        # Plot the data
        plt.plot(x_data, history, marker='braille', color='green')
        
        # Configure axes
        plt.ylim(0, 100)
        plt.xlabel("Time (2s intervals)")
        plt.ylabel("Load %")
        plt.title("GPU Utilization")
        
        # Set size for the plot
        plt.plotsize(60, 10)
        
        # Build the plot string
        return plt.build()
        
    def render(self) -> RenderableType:
        """Render GPU widget with stats and graphs.
        
        Returns:
            Panel containing GPU information or "N/A" message
        """
        if self.data is None:
            # GPU not available - show N/A
            text = Text("GPU: N/A", style="dim yellow")
            text.append("\n\nNo GPU detected or GPUtil not available.", style="dim")
            return Panel(
                text,
                title="[bold cyan]GPU[/bold cyan]",
                border_style="cyan"
            )
        
        # GPU is available - display stats
        table = Table.grid(padding=(0, 2))
        table.add_column(justify="left", no_wrap=True)
        table.add_column(justify="left")
        
        for gpu in self.data:
            # GPU name header
            table.add_row(
                Text(f"GPU {gpu['id']}: {gpu['name']}", style="bold cyan")
            )
            table.add_row("")
            
            # GPU Utilization
            load_pct = gpu['load']
            load_bar = self._create_progress_bar(load_pct, 30)
            table.add_row(
                Text("Utilization:", style="bold"),
                Text(f"{load_bar} {format_percentage(load_pct)}")
            )
            
            # Memory Usage
            mem_used = gpu['memory_used']
            mem_total = gpu['memory_total']
            mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
            mem_bar = self._create_progress_bar(mem_pct, 30)
            table.add_row(
                Text("Memory:", style="bold"),
                Text(f"{mem_bar} {format_bytes(mem_used * 1024 * 1024)} / {format_bytes(mem_total * 1024 * 1024)}")
            )
            
            # Temperature
            temp = gpu['temperature']
            temp_color = self._get_temp_color(temp)
            table.add_row(
                Text("Temperature:", style="bold"),
                Text(f"{temp:.1f}°C", style=temp_color)
            )
            
            table.add_row("")
        
        # Add graph if history available
        if self.monitor.get_history():
            graph = self._create_graph()
            table.add_row(Text(graph, style="dim"))
        
        return Panel(
            table,
            title="[bold cyan]GPU[/bold cyan]",
            border_style="cyan"
        )
    
    def _create_progress_bar(self, percent: float, width: int = 30) -> str:
        """Create a text-based progress bar.
        
        Args:
            percent: Percentage value (0-100)
            width: Width of the bar in characters
            
        Returns:
            String representation of the progress bar
        """
        filled = int((percent / 100) * width)
        empty = width - filled
        
        # Choose color based on percentage
        if percent < 50:
            color = "green"
        elif percent < 80:
            color = "yellow"
        else:
            color = "red"
        
        bar = "█" * filled + "░" * empty
        return f"[{color}]{bar}[/{color}]"
    
    def _get_temp_color(self, temp: float) -> str:
        """Get color style based on temperature.
        
        Args:
            temp: Temperature in Celsius
            
        Returns:
            Rich style string for the temperature
        """
        if temp < 60:
            return "green"
        elif temp < 75:
            return "yellow"
        elif temp < 85:
            return "orange"
        else:
            return "red bold"
