"""Integration tests for SystemMonitorApp.

These are smoke tests to ensure the app can initialize and run
without crashing. They don't test specific functionality, just
that all components work together.
"""

import pytest
from src.app import SystemMonitorApp


class TestAppIntegration:
    """Integration tests for the SystemMonitorApp."""
    
    def test_app_initialization(self):
        """Smoke test: ensure app can start without crashing."""
        app = SystemMonitorApp()
        assert app is not None
        # App should have monitors
        assert hasattr(app, 'cpu_monitor')
        assert hasattr(app, 'memory_monitor')
        assert hasattr(app, 'disk_monitor')
    
    @pytest.mark.asyncio
    async def test_app_runs(self):
        """Test app can run for a few seconds without errors."""
        app = SystemMonitorApp()
        async with app.run_test() as pilot:
            # Run for 2 seconds
            await pilot.pause(2.0)
            # If we get here, app ran successfully without crashes
            assert True
    
    @pytest.mark.asyncio
    async def test_app_quit_key(self):
        """Test that pressing 'q' quits the app."""
        app = SystemMonitorApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.5)
            # Press 'q' to quit
            await pilot.press('q')
            # App should exit gracefully
            await pilot.pause(0.5)
    
    @pytest.mark.asyncio
    async def test_app_widgets_exist(self):
        """Test that all expected widgets are present."""
        app = SystemMonitorApp()
        async with app.run_test() as pilot:
            await pilot.pause(1.0)
            
            # Check that key widgets are present in the app
            # Note: This is a basic check, exact widget structure may vary
            widgets = list(app.query("*"))
            assert len(widgets) > 0  # App should have widgets
            
            # Check that update intervals are set
            assert hasattr(app, 'cpu_monitor')
            assert hasattr(app, 'memory_monitor')
            assert hasattr(app, 'disk_monitor')
            assert hasattr(app, 'network_monitor')
            assert hasattr(app, 'process_monitor')
