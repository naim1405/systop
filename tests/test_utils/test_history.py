"""Tests for CircularBuffer class."""

import pytest
from threading import Thread
from src.utils.history import CircularBuffer


class TestCircularBufferInitialization:
    """Test buffer initialization."""
    
    def test_default_initialization(self):
        """Test default maxsize of 60."""
        buffer = CircularBuffer()
        assert buffer.maxsize == 60
        assert len(buffer) == 0
    
    def test_custom_maxsize(self):
        """Test custom maxsize."""
        buffer = CircularBuffer(maxsize=10)
        assert buffer.maxsize == 10
        assert len(buffer) == 0
    
    def test_invalid_maxsize(self):
        """Test that maxsize < 1 raises ValueError."""
        with pytest.raises(ValueError):
            CircularBuffer(maxsize=0)
        
        with pytest.raises(ValueError):
            CircularBuffer(maxsize=-1)


class TestCircularBufferAppend:
    """Test append operations."""
    
    def test_append_single_value(self):
        """Test appending a single value."""
        buffer = CircularBuffer(maxsize=5)
        buffer.append(1.0)
        assert len(buffer) == 1
        assert buffer.get_all() == [1.0]
    
    def test_append_multiple_values(self):
        """Test appending multiple values."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(3):
            buffer.append(i)
        assert len(buffer) == 3
        assert buffer.get_all() == [0, 1, 2]
    
    def test_append_overflow(self):
        """Test that oldest values are removed when buffer is full."""
        buffer = CircularBuffer(maxsize=3)
        for i in range(5):
            buffer.append(i)
        assert len(buffer) == 3
        assert buffer.get_all() == [2, 3, 4]
    
    def test_append_exact_capacity(self):
        """Test filling buffer to exact capacity."""
        buffer = CircularBuffer(maxsize=3)
        buffer.append(1)
        buffer.append(2)
        buffer.append(3)
        assert len(buffer) == 3
        assert buffer.get_all() == [1, 2, 3]
    
    def test_append_different_types(self):
        """Test appending different data types."""
        buffer = CircularBuffer(maxsize=5)
        buffer.append(1)
        buffer.append(1.5)
        buffer.append("text")
        buffer.append(None)
        buffer.append([1, 2])
        assert len(buffer) == 5
        assert buffer.get_all() == [1, 1.5, "text", None, [1, 2]]


class TestCircularBufferRetrieval:
    """Test data retrieval operations."""
    
    def test_get_all_empty(self):
        """Test get_all on empty buffer."""
        buffer = CircularBuffer(maxsize=5)
        assert buffer.get_all() == []
    
    def test_get_all_returns_copy(self):
        """Test that get_all returns a copy, not reference."""
        buffer = CircularBuffer(maxsize=5)
        buffer.append(1)
        buffer.append(2)
        data1 = buffer.get_all()
        data2 = buffer.get_all()
        assert data1 == data2
        assert data1 is not data2  # Different objects
    
    def test_get_last_n_partial(self):
        """Test getting last n values when n < buffer size."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(5):
            buffer.append(i)
        assert buffer.get_last_n(3) == [2, 3, 4]
    
    def test_get_last_n_all(self):
        """Test getting last n when n >= buffer size."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(3):
            buffer.append(i)
        assert buffer.get_last_n(5) == [0, 1, 2]
        assert buffer.get_last_n(10) == [0, 1, 2]
    
    def test_get_last_n_zero(self):
        """Test getting last 0 values."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(3):
            buffer.append(i)
        assert buffer.get_last_n(0) == []
    
    def test_get_last_n_negative(self):
        """Test getting last n with negative n."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(3):
            buffer.append(i)
        assert buffer.get_last_n(-1) == []
    
    def test_get_last_n_empty_buffer(self):
        """Test get_last_n on empty buffer."""
        buffer = CircularBuffer(maxsize=5)
        assert buffer.get_last_n(3) == []


class TestCircularBufferClear:
    """Test clear operation."""
    
    def test_clear_empty(self):
        """Test clearing empty buffer."""
        buffer = CircularBuffer(maxsize=5)
        buffer.clear()
        assert len(buffer) == 0
        assert buffer.get_all() == []
    
    def test_clear_filled(self):
        """Test clearing filled buffer."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(5):
            buffer.append(i)
        buffer.clear()
        assert len(buffer) == 0
        assert buffer.get_all() == []
    
    def test_clear_and_reuse(self):
        """Test using buffer after clearing."""
        buffer = CircularBuffer(maxsize=3)
        for i in range(3):
            buffer.append(i)
        buffer.clear()
        buffer.append(10)
        buffer.append(20)
        assert buffer.get_all() == [10, 20]


class TestCircularBufferThreadSafety:
    """Test thread safety of buffer operations."""
    
    def test_concurrent_appends(self):
        """Test multiple threads appending concurrently."""
        buffer = CircularBuffer(maxsize=100)
        
        def append_values(start, count):
            for i in range(start, start + count):
                buffer.append(i)
        
        threads = []
        for i in range(5):
            t = Thread(target=append_values, args=(i * 20, 20))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have 100 values (buffer is full)
        assert len(buffer) == 100
        data = buffer.get_all()
        assert len(data) == 100
    
    def test_concurrent_read_write(self):
        """Test concurrent reads and writes."""
        buffer = CircularBuffer(maxsize=50)
        results = []
        
        def writer():
            for i in range(100):
                buffer.append(i)
        
        def reader():
            for _ in range(10):
                results.append(len(buffer.get_all()))
        
        write_thread = Thread(target=writer)
        read_threads = [Thread(target=reader) for _ in range(3)]
        
        write_thread.start()
        for t in read_threads:
            t.start()
        
        write_thread.join()
        for t in read_threads:
            t.join()
        
        # Should complete without errors
        assert len(buffer) == 50  # Buffer capped at maxsize


class TestCircularBufferEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_buffer_size_one(self):
        """Test buffer with maxsize of 1."""
        buffer = CircularBuffer(maxsize=1)
        buffer.append(1)
        assert buffer.get_all() == [1]
        buffer.append(2)
        assert buffer.get_all() == [2]
    
    def test_large_buffer(self):
        """Test large buffer size."""
        buffer = CircularBuffer(maxsize=10000)
        for i in range(10000):
            buffer.append(i)
        assert len(buffer) == 10000
        assert buffer.get_all()[0] == 0
        assert buffer.get_all()[-1] == 9999
    
    def test_get_last_n_equals_size(self):
        """Test get_last_n when n equals buffer size."""
        buffer = CircularBuffer(maxsize=5)
        for i in range(5):
            buffer.append(i)
        assert buffer.get_last_n(5) == [0, 1, 2, 3, 4]
