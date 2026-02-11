"""
Unit tests for chipclaw.bus.events module
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chipclaw.bus.events import InboundMessage, OutboundMessage


def test_inbound_message_creation():
    """Test InboundMessage creation"""
    msg = InboundMessage(
        channel="test",
        sender_id="user123",
        chat_id="chat123",
        content="Hello, world!"
    )
    assert msg.channel == "test"
    assert msg.sender_id == "user123"
    assert msg.chat_id == "chat123"
    assert msg.content == "Hello, world!"
    assert msg.metadata == {}


def test_inbound_message_with_metadata():
    """Test InboundMessage with metadata"""
    metadata = {"key": "value", "number": 42}
    msg = InboundMessage(
        channel="mqtt",
        sender_id="user456",
        chat_id="chat456",
        content="Test message",
        metadata=metadata
    )
    assert msg.metadata == metadata
    assert msg.metadata["key"] == "value"
    assert msg.metadata["number"] == 42


def test_outbound_message_creation():
    """Test OutboundMessage creation"""
    msg = OutboundMessage(
        channel="uart",
        chat_id="chat789",
        content="Response message"
    )
    assert msg.channel == "uart"
    assert msg.chat_id == "chat789"
    assert msg.content == "Response message"
    assert msg.metadata == {}


def test_outbound_message_with_metadata():
    """Test OutboundMessage with metadata"""
    metadata = {"status": "ok", "timestamp": 1234567890}
    msg = OutboundMessage(
        channel="mqtt",
        chat_id="chat100",
        content="Status update",
        metadata=metadata
    )
    assert msg.metadata == metadata
    assert msg.metadata["status"] == "ok"


def test_message_representation():
    """Test message string representation"""
    msg = InboundMessage(
        channel="test",
        sender_id="user1",
        chat_id="chat1",
        content="Test"
    )
    # Should be able to convert to string without error
    str_repr = str(msg)
    assert isinstance(str_repr, str)
    assert "InboundMessage" in str_repr


def test_session_key():
    """Test session key generation"""
    msg = InboundMessage(
        channel="mqtt",
        sender_id="user1",
        chat_id="room123",
        content="Test"
    )
    assert msg.session_key == "mqtt:room123"


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
