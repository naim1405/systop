"""Process widget for displaying and managing system processes.

This module provides the ProcessWidget class that displays a paginated,
searchable, and interactive process table with sorting and kill capabilities.
"""

from typing import Optional, Dict, Any, List
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from src.monitors.processes import ProcessMonitor
from src.config import config


class ProcessWidget(Widget):
    """Widget for displaying and managing system processes.
    
    Displays an interactive, paginated table of all running processes with
    support for:
    - Pagination (configurable page size)
    - Real-time search/filtering by process name
    - Sorting by various columns
    - Process selection with arrow keys
    - Killing selected processes with confirmation
    - Keyboard navigation (arrow keys, page up/down)
    
    This is the most complex widget in systop, featuring full interactivity
    and state management.
    
    Attributes:
        monitor: ProcessMonitor instance for data collection
        current_page: Current page number (0-indexed)
        search_term: Current search filter string
        sort_by: Field to sort processes by
        selected_row: Index of currently selected process on current page
        can_focus: Widget can receive keyboard focus
        
    Keyboard Bindings:
        k: Kill selected process (with confirmation)
        /: Activate search mode
        up/down: Navigate process list
        pageup/pagedown: Navigate pages
        enter: Apply search filter
        escape: Clear search and return to normal mode
        
    Example:
        monitor = ProcessMonitor()
        widget = ProcessWidget(monitor)
    """
    
    # Reactive attributes for state management
    current_page: int = reactive(0)
    search_term: str = reactive("")
    sort_by: str = reactive("cpu_percent")
    selected_row: int = reactive(0)
    
    # Internal state
    _search_active: bool = False
    _search_input: str = ""
    _confirm_kill: bool = False
    _kill_pid: Optional[int] = None
    _kill_name: Optional[str] = None
    _message: Optional[str] = None
    _message_type: str = "info"  # 'info', 'success', 'error'
    
    def __init__(self, monitor: ProcessMonitor, **kwargs):
        """Initialize process widget with a monitor.
        
        Args:
            monitor: ProcessMonitor instance to collect data from
            **kwargs: Additional arguments passed to Widget
        """
        super().__init__(**kwargs)
        self.monitor = monitor
        self.can_focus = True  # Enable keyboard input
        self.page_size = config.PROCESS_PAGE_SIZE
        self.sort_by = config.PROCESS_SORT_BY
        
        # Cache for current data
        self._all_processes: List[Dict[str, Any]] = []
        self._filtered_processes: List[Dict[str, Any]] = []
        self._total_count: int = 0
        
    def on_mount(self) -> None:
        """Start periodic data updates when widget is mounted."""
        self.set_interval(2.0, self.refresh_data)
        # Initial data fetch
        self.refresh_data()
        
    def refresh_data(self) -> None:
        """Fetch new process data and update display."""
        # Collect all processes with current sort order
        data = self.monitor.collect(sort_by=self.sort_by, reverse=True)
        self._all_processes = data['processes']
        self._total_count = data['total_count']
        
        # Apply search filter if active
        self._apply_filter()
        
        # Validate current page and selection
        self._validate_state()
        
    def _apply_filter(self) -> None:
        """Apply search filter to process list."""
        if self.search_term.strip():
            # Filter processes by name containing search term (case-insensitive)
            search_lower = self.search_term.lower()
            self._filtered_processes = [
                p for p in self._all_processes
                if search_lower in p['name'].lower()
            ]
        else:
            # No filter, show all processes
            self._filtered_processes = self._all_processes
            
    def _validate_state(self) -> None:
        """Validate and correct page number and selection."""
        # Calculate total pages
        total_pages = self._get_total_pages()
        
        # Fix page number if out of bounds
        if total_pages == 0:
            self.current_page = 0
        elif self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
            
        # Fix selected row if out of bounds
        page_processes = self._get_current_page_processes()
        if page_processes and self.selected_row >= len(page_processes):
            self.selected_row = max(0, len(page_processes) - 1)
        elif not page_processes:
            self.selected_row = 0
            
    def _get_total_pages(self) -> int:
        """Calculate total number of pages."""
        if not self._filtered_processes:
            return 0
        return (len(self._filtered_processes) + self.page_size - 1) // self.page_size
    
    def _get_current_page_processes(self) -> List[Dict[str, Any]]:
        """Get processes for the current page."""
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self._filtered_processes[start:end]
    
    def _get_selected_process(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected process."""
        page_processes = self._get_current_page_processes()
        if page_processes and 0 <= self.selected_row < len(page_processes):
            return page_processes[self.selected_row]
        return None
    
    def on_key(self, event) -> None:
        """Handle keyboard input.
        
        Args:
            event: Keyboard event from Textual
        """
        # Handle confirmation dialog
        if self._confirm_kill:
            if event.key == "y":
                self._execute_kill()
                event.prevent_default()
                return
            elif event.key == "n" or event.key == "escape":
                self._cancel_kill()
                event.prevent_default()
                return
        
        # Handle search mode
        if self._search_active:
            if event.key == "enter":
                self._apply_search()
                event.prevent_default()
                return
            elif event.key == "escape":
                self._cancel_search()
                event.prevent_default()
                return
            elif event.key == "backspace":
                self._search_input = self._search_input[:-1]
                event.prevent_default()
                return
            elif len(event.key) == 1 and event.key.isprintable():
                self._search_input += event.key
                event.prevent_default()
                return
        
        # Normal mode key handlers
        if event.key == "k":
            self._initiate_kill()
            event.prevent_default()
        elif event.key == "slash":  # '/' key
            self._activate_search()
            event.prevent_default()
        elif event.key == "up":
            self._move_selection(-1)
            event.prevent_default()
        elif event.key == "down":
            self._move_selection(1)
            event.prevent_default()
        elif event.key == "pageup":
            self._previous_page()
            event.prevent_default()
        elif event.key == "pagedown":
            self._next_page()
            event.prevent_default()
        elif event.key == "home":
            self._first_page()
            event.prevent_default()
        elif event.key == "end":
            self._last_page()
            event.prevent_default()
        elif event.key == "escape":
            # Clear any message
            self._message = None
            
    def _move_selection(self, delta: int) -> None:
        """Move selection up or down.
        
        Args:
            delta: Number of rows to move (-1 for up, 1 for down)
        """
        page_processes = self._get_current_page_processes()
        if not page_processes:
            return
            
        new_row = self.selected_row + delta
        
        # Wrap around within current page
        if new_row < 0:
            # Try to go to previous page
            if self.current_page > 0:
                self._previous_page()
                self.selected_row = self.page_size - 1
                self._validate_state()
            else:
                # Stay at top
                self.selected_row = 0
        elif new_row >= len(page_processes):
            # Try to go to next page
            if self.current_page < self._get_total_pages() - 1:
                self._next_page()
                self.selected_row = 0
            else:
                # Stay at bottom
                self.selected_row = len(page_processes) - 1
        else:
            self.selected_row = new_row
            
    def _previous_page(self) -> None:
        """Navigate to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.selected_row = 0
            
    def _next_page(self) -> None:
        """Navigate to next page."""
        if self.current_page < self._get_total_pages() - 1:
            self.current_page += 1
            self.selected_row = 0
            
    def _first_page(self) -> None:
        """Navigate to first page."""
        self.current_page = 0
        self.selected_row = 0
        
    def _last_page(self) -> None:
        """Navigate to last page."""
        total_pages = self._get_total_pages()
        if total_pages > 0:
            self.current_page = total_pages - 1
            self.selected_row = 0
            
    def _activate_search(self) -> None:
        """Activate search mode."""
        self._search_active = True
        self._search_input = self.search_term
        self._message = None
        
    def _cancel_search(self) -> None:
        """Cancel search mode without applying."""
        self._search_active = False
        self._search_input = ""
        
    def _apply_search(self) -> None:
        """Apply search filter."""
        self.search_term = self._search_input.strip()
        self._search_active = False
        self._search_input = ""
        
        # Reapply filter and reset to first page
        self._apply_filter()
        self.current_page = 0
        self.selected_row = 0
        self._validate_state()
        
        # Show search result message
        if self.search_term:
            count = len(self._filtered_processes)
            self._message = f"Found {count} processes matching '{self.search_term}'"
            self._message_type = "info"
        
    def _initiate_kill(self) -> None:
        """Initiate process kill with confirmation."""
        process = self._get_selected_process()
        if not process:
            self._message = "No process selected"
            self._message_type = "error"
            return
            
        self._confirm_kill = True
        self._kill_pid = process['pid']
        self._kill_name = process['name']
        self._message = None
        
    def _execute_kill(self) -> None:
        """Execute process kill."""
        if self._kill_pid is None:
            self._cancel_kill()
            return
            
        success = self.monitor.kill_process(self._kill_pid)
        
        if success:
            self._message = f"Killed process '{self._kill_name}' (PID: {self._kill_pid})"
            self._message_type = "success"
        else:
            self._message = f"Failed to kill process (permission denied or not found)"
            self._message_type = "error"
            
        self._cancel_kill()
        self.refresh_data()
        
    def _cancel_kill(self) -> None:
        """Cancel process kill."""
        self._confirm_kill = False
        self._kill_pid = None
        self._kill_name = None
        
    def render(self) -> RenderableType:
        """Render the process widget.
        
        Returns:
            Rich renderable (Panel with process table)
        """
        # Build content
        content_parts = []
        
        # Show confirmation dialog if active
        if self._confirm_kill:
            confirm_text = Text()
            confirm_text.append("\n⚠️  ", style="bold yellow")
            confirm_text.append(f"Kill process '{self._kill_name}' (PID: {self._kill_pid})?\n", style="bold")
            confirm_text.append("Press 'y' to confirm, 'n' or ESC to cancel\n", style="dim")
            return Panel(confirm_text, title="Confirm Kill", border_style="yellow")
        
        # Show search box if active
        if self._search_active:
            search_text = Text()
            search_text.append("Search: ", style="cyan bold")
            search_text.append(self._search_input, style="white")
            search_text.append("_", style="white blink")
            search_text.append("\n(Enter to apply, ESC to cancel)", style="dim")
            content_parts.append(search_text)
            content_parts.append("\n")
        
        # Show message if present
        if self._message:
            msg_text = Text()
            if self._message_type == "success":
                msg_text.append(f"✓ {self._message}", style="green")
            elif self._message_type == "error":
                msg_text.append(f"✗ {self._message}", style="red")
            else:
                msg_text.append(f"ℹ {self._message}", style="cyan")
            content_parts.append(msg_text)
            content_parts.append("\n\n")
        
        # Get current page processes
        page_processes = self._get_current_page_processes()
        
        if not page_processes:
            no_data = Text("No processes found", style="dim")
            if self.search_term:
                no_data.append(f" matching '{self.search_term}'", style="yellow")
            content_parts.append(no_data)
        else:
            # Create process table
            table = Table(show_header=True, box=None, padding=(0, 1))
            table.add_column("", width=2, style="dim")  # Selection indicator
            table.add_column("PID", justify="right", style="cyan", width=8)
            table.add_column("Name", style="white", width=30, no_wrap=True)
            table.add_column("User", style="blue", width=15, no_wrap=True)
            table.add_column("CPU%", justify="right", style="yellow", width=7)
            table.add_column("MEM%", justify="right", style="magenta", width=7)
            table.add_column("Status", style="green", width=10)
            
            # Add process rows
            for idx, proc in enumerate(page_processes):
                # Highlight selected row
                indicator = "→" if idx == self.selected_row else ""
                row_style = "bold" if idx == self.selected_row else ""
                
                table.add_row(
                    indicator,
                    str(proc['pid']),
                    proc['name'][:28],  # Truncate long names
                    proc['user'][:13],  # Truncate long usernames
                    f"{proc['cpu_percent']:.1f}",
                    f"{proc['memory_percent']:.1f}",
                    proc['status'],
                    style=row_style
                )
            
            content_parts.append(table)
        
        # Add page indicator
        total_pages = self._get_total_pages()
        page_info = Text()
        page_info.append("\n", style="dim")
        
        if total_pages > 0:
            page_info.append(
                f"Page {self.current_page + 1}/{total_pages}  ", 
                style="cyan"
            )
        
        page_info.append(f"Total: {len(self._filtered_processes)} processes", style="dim")
        
        if self.search_term:
            page_info.append(f" (filtered from {self._total_count})", style="dim")
            
        content_parts.append(page_info)
        
        # Add keybindings help
        help_text = Text()
        help_text.append("\n", style="dim")
        help_text.append("k", style="bold")
        help_text.append(":kill ", style="dim")
        help_text.append("/", style="bold")
        help_text.append(":search ", style="dim")
        help_text.append("↑↓", style="bold")
        help_text.append(":navigate ", style="dim")
        help_text.append("PgUp/PgDn", style="bold")
        help_text.append(":page ", style="dim")
        help_text.append("ESC", style="bold")
        help_text.append(":clear", style="dim")
        content_parts.append(help_text)
        
        # Combine all parts
        from rich.console import Group
        content = Group(*content_parts)
        
        # Create panel
        title = "Processes"
        if self.search_term:
            title += f" [filtered: {self.search_term}]"
        
        return Panel(
            content,
            title=title,
            border_style="green" if self.has_focus else "blue"
        )
