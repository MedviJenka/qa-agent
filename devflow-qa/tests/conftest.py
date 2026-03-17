"""
Shared pytest fixtures for the Todo App Playwright test suite.

Requirements:
    pip install pytest-playwright
    playwright install chromium

Run all tests:
    pytest tests/ --base-url http://localhost:5173

Run a single suite:
    pytest tests/sanity/ --base-url http://localhost:5173
"""

import pytest


# pytest-playwright automatically provides the `page` fixture.
# The BASE_URL below is the default dev-server address; override at runtime with:
#   pytest --base-url http://localhost:5173
#
# If pytest-playwright is installed, its `browser`, `context`, and `page`
# fixtures are available with no extra configuration here.


def pytest_configure(config):
    """Register custom markers so pytest --strict-markers does not fail."""
    config.addinivalue_line("markers", "sanity: basic render / smoke checks")
    config.addinivalue_line("markers", "critical_flow: end-to-end user flow tests")
    config.addinivalue_line("markers", "regression: regression guard tests for known findings")
    config.addinivalue_line("markers", "edge_case: loading, error, and empty-state tests")
