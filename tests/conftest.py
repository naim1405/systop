"""Pytest configuration for the systop project.

This ensures the project root is on sys.path so that imports like
`from src.app import SystemMonitorApp` work reliably under pytest,
regardless of how the tests are invoked.
"""

from __future__ import annotations

import os
import sys

# Determine the project root (one level up from the tests directory)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# Prepend project root to sys.path if it's not already present
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
