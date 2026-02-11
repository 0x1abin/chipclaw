"""
Integration test example for ChipClaw message bus
This demonstrates testing async components
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from chipclaw.bus.queue import MessageBus
from chipclaw.bus.events import InboundMessage, OutboundMessage


def run_async_test(test_func):
    """Helper to run async test functions with proper event loop setup"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_func())
    finally:
        loop.close()


def test_message_bus_inbound():
    """Test message bus inbound message handling"""
    async def run_test():
        bus = MessageBus()
        
        # Create test message
        test_msg = InboundMessage(
            channel="test",
            sender_id="user1",
            chat_id="chat1",
            content="Hello"
        )
        
        # Publish to inbound queue
        await bus.publish_inbound(test_msg)
        
        # Consume from inbound queue
        msg = await bus.consume_inbound()
        
        # Verify message
        assert msg.content == "Hello"
        assert msg.channel == "test"
        assert msg.sender_id == "user1"
        assert msg.chat_id == "chat1"
    
    run_async_test(run_test)


def test_message_bus_outbound_subscribe():
    """Test message bus outbound subscription"""
    async def run_test():
        bus = MessageBus()
        received_messages = []
        
        # Subscribe to outbound messages for a channel
        async def handler(msg):
            received_messages.append(msg)
        
        bus.subscribe_outbound("test_channel", handler)
        
        # Check subscription was registered
        assert "test_channel" in bus.subscribers
        assert bus.subscribers["test_channel"] == handler
    
    run_async_test(run_test)


def test_message_bus_multiple_messages():
    """Test multiple messages through the bus"""
    async def run_test():
        bus = MessageBus()
        
        # Publish multiple messages
        for i in range(3):
            msg = InboundMessage(
                channel="test",
                sender_id=f"user{i}",
                chat_id="chat1",
                content=f"Message {i}"
            )
            await bus.publish_inbound(msg)
        
        # Consume and verify
        for i in range(3):
            msg = await bus.consume_inbound()
            assert msg.content == f"Message {i}"
            assert msg.sender_id == f"user{i}"
    
    run_async_test(run_test)


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
