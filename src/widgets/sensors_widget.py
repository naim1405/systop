"""Temperature sensors widget for displaying sensor data in the TUI.

This module provides the SensorsWidget class that visualizes temperature readings
from all available hardware sensors. Gracefully hides itself when sensors are 
unavailable (e.g., on VMs or systems without sensor support).

Note: Sensor availability varies by system and platform.
"""

from typing import Optional, Dict, List, Any
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.monitors.sensors import SensorsMonitor


class SensorsWidget(Widget):
    """Widget for displaying temperature sensor information.
    
    Displays real-time temperature readings from all available sensors including:
    - Sensor type (coretemp, acpitz, etc.)
    - Sensor label
    - Current temperature
    - High threshold
    - Critical threshold
    
    Returns empty string (hides widget) when no sensors are available.
    
    Attributes:
        data: Reactive property storing current sensor readings (None if unavailable)
        monitor: SensorsMonitor instance for data collection
        
    Example:
        sensors_monitor = SensorsMonitor()
        sensors_widget = SensorsWidget(sensors_monitor)
    """
    
    data: Optional[Dict[str, List[Dict[str, Any]]]] = reactive(None)
    
    def __init__(self, monitor: SensorsMonitor, **kwargs):
        """Initialize sensors widget with a monitor.
        
        Args:
            monitor: SensorsMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        # Update every 5 seconds for sensors (less frequent updates)
        self.set_interval(5.0, self.refresh_data)
        # Initial data fetch
        self.refresh_data()
        
    def refresh_data(self) -> None:
        """Fetch new data from monitor and trigger re-render."""
        try:
            self.data = self.monitor.collect()
        except Exception as e:
            self.data = {'error': str(e)}
    
    def render(self) -> RenderableType:
        """Render temperature sensors widget with readings.
        
        Returns:
            Empty string if sensors unavailable (widget hidden),
            otherwise Panel containing sensor information table
        """
        # Handle error state
        if self.data and 'error' in self.data:
            return Panel(
                Text(f"Error: {self.data['error']}", style="red"),
                title="[bold red]Sensors - Error[/bold red]",
                border_style="red"
            )
        
        if self.data is None or not self.data:
            # Sensors not available - return empty string to hide widget
            return ""
        
        try:
            # Sensors are available - display readings in a table
            table = Table(show_header=True, header_style="bold cyan", box=None)
            table.add_column("Sensor", style="cyan", no_wrap=True)
            table.add_column("Label", style="white")
            table.add_column("Current", justify="right", style="white")
            table.add_column("High", justify="right", style="yellow")
            table.add_column("Critical", justify="right", style="red")
            
            # Add rows for each sensor grouped by type
            for sensor_type, sensors in sorted(self.data.items()):
                for idx, sensor in enumerate(sensors):
                    # Only show sensor type name for the first sensor of each type
                    type_display = sensor_type if idx == 0 else ""
                    
                    # Get current temperature and apply color coding
                    current_temp = sensor['current']
                    high_temp = sensor['high']
                    critical_temp = sensor['critical']
                    
                    # Color code current temperature based on thresholds
                    temp_color = self._get_temp_color(current_temp, high_temp, critical_temp)
                    current_display = Text(f"{current_temp:.1f}°C", style=temp_color)
                    
                    # Format high and critical temps (may be None)
                    high_display = f"{high_temp:.1f}°C" if high_temp is not None else "N/A"
                    critical_display = f"{critical_temp:.1f}°C" if critical_temp is not None else "N/A"
                    
                    table.add_row(
                        type_display,
                        sensor['label'],
                        current_display,
                        high_display,
                        critical_display
                    )
            
            return Panel(
                table,
                title="[bold magenta]Temperature Sensors[/bold magenta]",
                border_style="magenta"
            )
        except Exception as e:
            return Panel(
                Text(f"Render error: {str(e)}", style="red"),
                title="[bold red]Sensors - Error[/bold red]",
                border_style="red"
            )
    
    def _get_temp_color(self, current: float, high: Optional[float], 
                        critical: Optional[float]) -> str:
        """Get color style based on temperature and thresholds.
        
        Args:
            current: Current temperature in Celsius
            high: High threshold temperature (None if not available)
            critical: Critical threshold temperature (None if not available)
            
        Returns:
            Rich style string for the temperature
        """
        # Use thresholds if available
        if critical is not None and current >= critical:
            return "red bold blink"
        elif critical is not None and current >= critical - 5:
            return "red bold"
        elif high is not None and current >= high:
            return "orange bold"
        elif high is not None and current >= high - 5:
            return "yellow"
        
        # Fallback to generic thresholds if no high/critical defined
        if current >= 90:
            return "red bold"
        elif current >= 80:
            return "orange bold"
        elif current >= 70:
            return "yellow"
        elif current >= 60:
            return "white"
        else:
            return "green"
