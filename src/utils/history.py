"""Circular buffer for storing time-series data efficiently."""

from collections import deque
from threading import Lock
from typing import List, Any


class CircularBuffer:
    """
    Thread-safe circular buffer with fixed size for storing time-series data.
    
    Automatically removes oldest values when full. Uses collections.deque
    for memory efficiency.
    
    Attributes:
        maxsize: Maximum number of elements the buffer can hold
        
    Example:
        >>> buffer = CircularBuffer(maxsize=3)
        >>> buffer.append(1.0)
        >>> buffer.append(2.0)
        >>> buffer.append(3.0)
        >>> buffer.get_all()
        [1.0, 2.0, 3.0]
        >>> buffer.append(4.0)  # Removes 1.0 automatically
        >>> buffer.get_all()
        [2.0, 3.0, 4.0]
    """
    
    def __init__(self, maxsize: int = 60):
        """
        Initialize buffer with max size.
        
        Args:
            maxsize: Maximum number of elements (default 60 for 1-minute history)
        
        Raises:
            ValueError: If maxsize is less than 1
        """
        if maxsize < 1:
            raise ValueError("maxsize must be at least 1")
        
        self._buffer = deque(maxlen=maxsize)
        self._lock = Lock()
        self._maxsize = maxsize
    
    def append(self, value: Any) -> None:
        """
        Add new value to buffer.
        
        Automatically removes oldest value if buffer is full.
        Thread-safe operation.
        
        Args:
            value: Value to add (typically float for metrics)
        """
        with self._lock:
            self._buffer.append(value)
    
    def get_all(self) -> List[Any]:
        """
        Return all values as list.
        
        Thread-safe operation. Returns a copy to prevent external modification.
        
        Returns:
            List of all values in buffer, oldest to newest
        """
        with self._lock:
            return list(self._buffer)
    
    def get_last_n(self, n: int) -> List[Any]:
        """
        Return last n values.
        
        Thread-safe operation. If n exceeds buffer size, returns all values.
        
        Args:
            n: Number of most recent values to return
            
        Returns:
            List of last n values, oldest to newest
            
        Example:
            >>> buffer = CircularBuffer(maxsize=5)
            >>> for i in range(5):
            ...     buffer.append(i)
            >>> buffer.get_last_n(3)
            [2, 3, 4]
        """
        with self._lock:
            if n <= 0:
                return []
            if n >= len(self._buffer):
                return list(self._buffer)
            return list(self._buffer)[-n:]
    
    def clear(self) -> None:
        """
        Clear all values from buffer.
        
        Thread-safe operation.
        """
        with self._lock:
            self._buffer.clear()
    
    def __len__(self) -> int:
        """Return current number of elements in buffer."""
        with self._lock:
            return len(self._buffer)
    
    @property
    def maxsize(self) -> int:
        """Return maximum buffer size."""
        return self._maxsize
