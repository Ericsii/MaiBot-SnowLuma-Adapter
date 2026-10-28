from importlib import import_module
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock

import sys

import pytest


PACKAGE = "sl_runtime_protocol_test"
package = ModuleType(PACKAGE)
package.__path__ = [str(Path(__file__).resolve().parents[1])]
sys.modules[PACKAGE] = package
QQRuntimeStateManager = import_module(f"{PACKAGE}.runtime_state").QQRuntimeStateManager


@pytest.mark.asyncio
async def test_protocol_detection_and_switch_are_reported():
    gateway = SimpleNamespace(update_state=AsyncMock(return_value=True))
    state = QQRuntimeStateManager(gateway, Mock(), "gateway")
    config = SimpleNamespace(connection_id="connection", build_ws_url=lambda: "ws://localhost")
    assert not await state.report_connected("bot", config)
    gateway.update_state.assert_not_awaited()
    for protocol in ("napcat", "snowluma"):
        state.detected_protocol = protocol
        assert await state.report_connected("bot", config)
        assert gateway.update_state.call_args.kwargs["metadata"]["protocol"] == protocol
        assert gateway.update_state.call_args.kwargs["platform"] == "qq"
    assert gateway.update_state.await_count == 2
    assert await state.report_connected("bot", config)
    assert gateway.update_state.await_count == 2
