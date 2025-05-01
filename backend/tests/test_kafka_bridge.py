import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import backend.kafka_service.kafka_ws_bridge as bridge

@pytest.mark.asyncio
async def test_notify_clients_sends_messages():
    mock_ws_1 = AsyncMock()
    mock_ws_2 = AsyncMock()

    bridge.connected_clients.clear()
    bridge.connected_clients.update({mock_ws_1, mock_ws_2})

    message = "Test message"
    await bridge.notify_clients(message)

    mock_ws_1.send_text.assert_awaited_once_with(message)
    mock_ws_2.send_text.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_notify_clients_removes_disconnected_clients():
    good_ws = AsyncMock()
    bad_ws = AsyncMock()
    bad_ws.send_text.side_effect = Exception("Disconnected")

    bridge.connected_clients.clear()
    bridge.connected_clients.update({good_ws, bad_ws})

    message = "Test message"
    await bridge.notify_clients(message)

    assert good_ws in bridge.connected_clients
    assert bad_ws not in bridge.connected_clients

@pytest.mark.asyncio
async def test_kafka_message_queues():
    msg = {
        "topic": "test",
        "key": "test-key",
        "value": {"foo": "bar"},
        "timestamp": 1234567890
    }

    queue = bridge.kafka_to_ws_queue
    queue._queue.clear()

    await queue.put(msg)
    queued_msg = await queue.get()

    assert queued_msg == msg

