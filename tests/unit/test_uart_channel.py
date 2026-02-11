"""
Unit tests for chipclaw.channels.uart module
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from chipclaw.channels.uart import UARTChannel
from chipclaw.bus.events import InboundMessage, OutboundMessage


class MockBus:
    """Mock message bus for testing"""
    def __init__(self):
        self.inbound_messages = []
    
    async def publish_inbound(self, msg):
        self.inbound_messages.append(msg)


def run_async_test(test_func):
    """Helper to run async test functions with proper event loop setup"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_func())
    finally:
        loop.close()


def test_uart_channel_creation():
    """Test UARTChannel creation with default config"""
    bus = MockBus()
    config = {"enabled": True}
    ch = UARTChannel(bus, config)
    assert ch.name == "uart"
    assert ch.buffer == ""
    assert ch._running is False
    assert ch._poller is None


def test_uart_channel_handle_line_plain_text():
    """Test handling plain text input"""
    async def run_test():
        bus = MockBus()
        config = {"enabled": True}
        ch = UARTChannel(bus, config)
        
        await ch._handle_line("hello world")
        
        assert len(bus.inbound_messages) == 1
        msg = bus.inbound_messages[0]
        assert msg.channel == "uart"
        assert msg.content == "hello world"
        assert msg.sender_id == "uart_user"
        assert msg.chat_id == "uart_default"
    
    run_async_test(run_test)


def test_uart_channel_handle_line_json():
    """Test handling JSON input"""
    async def run_test():
        bus = MockBus()
        config = {"enabled": True}
        ch = UARTChannel(bus, config)
        
        json_line = json.dumps({
            "content": "test message",
            "sender_id": "user1",
            "chat_id": "chat1"
        })
        await ch._handle_line(json_line)
        
        assert len(bus.inbound_messages) == 1
        msg = bus.inbound_messages[0]
        assert msg.channel == "uart"
        assert msg.content == "test message"
        assert msg.sender_id == "user1"
        assert msg.chat_id == "chat1"
    
    run_async_test(run_test)


def test_uart_channel_send():
    """Test sending an outbound message via stdout"""
    import io
    
    async def run_test():
        bus = MockBus()
        config = {"enabled": True}
        ch = UARTChannel(bus, config)
        
        out_msg = OutboundMessage(
            channel="uart",
            chat_id="chat1",
            content="response text"
        )
        
        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            await ch.send(out_msg)
        finally:
            sys.stdout = old_stdout
        
        output = captured.getvalue()
        data = json.loads(output.strip())
        assert data["content"] == "response text"
        assert data["chat_id"] == "chat1"
    
    run_async_test(run_test)


def test_uart_channel_stop():
    """Test stopping the channel"""
    async def run_test():
        bus = MockBus()
        config = {"enabled": True}
        ch = UARTChannel(bus, config)
        ch._running = True
        
        await ch.stop()
        
        assert ch._running is False
    
    run_async_test(run_test)


def test_uart_channel_no_machine_uart():
    """Test that UARTChannel does not depend on machine.UART"""
    import chipclaw.channels.uart as uart_mod
    # Should not have UART_AVAILABLE or reference to machine
    assert not hasattr(uart_mod, 'UART_AVAILABLE')


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
