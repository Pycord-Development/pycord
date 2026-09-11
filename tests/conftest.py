import asyncio

import pytest


@pytest.fixture(autouse=True)
def _reset_event_loop_policy():
    # pytest-asyncio calls per-test asyncio.set_event_loop(None) at the end
    # but doesn't reset the event loop policy so we do it here or else it breaks on py <3.14
    yield
    asyncio.set_event_loop_policy(None)
