"""
Playwright configuration for pytest
"""

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Configure browser context
    """
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "locale": "ja-JP",
        "timezone_id": "Asia/Tokyo",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """
    Configure browser launch arguments
    """
    return {
        **browser_type_launch_args,
        "headless": True,  # Set to False for debugging
        "slow_mo": 0,  # Slow down operations (milliseconds)
    }
