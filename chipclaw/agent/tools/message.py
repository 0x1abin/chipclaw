"""
ChipClaw Message Tool
Send messages to channels
"""
from .base import Tool


class MessageTool(Tool):
    """Send message to a channel"""
    
    name = "send_message"
    description = "Send a message to a channel (defaults to current conversation context)"
    parameters = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Message content to send"
            },
            "channel": {
                "type": "string",
                "description": "Target channel name (optional, defaults to current channel)"
            },
            "chat_id": {
                "type": "string",
                "description": "Target chat ID (optional, defaults to current chat)"
            }
        },
        "required": ["content"]
    }
    
    def __init__(self, bus):
        self.bus = bus
        self.default_channel = None
        self.default_chat_id = None
    
    def set_context(self, channel, chat_id):
        """Set default channel and chat_id from current conversation"""
        self.default_channel = channel
        self.default_chat_id = chat_id
    
    def execute(self, content, channel=None, chat_id=None):
        """Send message via bus"""
        try:
            import uasyncio as asyncio
        except ImportError:
            import asyncio
        
        from ...bus.events import OutboundMessage
        
        # Use defaults if not specified
        target_channel = channel or self.default_channel
        target_chat_id = chat_id or self.default_chat_id
        
        if not target_channel or not target_chat_id:
            return "Error: No channel or chat_id specified and no default context set"
        
        # Create outbound message
        msg = OutboundMessage(
            channel=target_channel,
            chat_id=target_chat_id,
            content=content
        )
        
        # Publish to bus (need to handle async)
        # Since execute() is not async, we create a task
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            loop.create_task(self.bus.publish_outbound(msg))
            return f"Message queued for {target_channel}:{target_chat_id}"
        except:
            # Fallback: direct await (might not work in sync context)
            return f"Error: Could not queue message (asyncio context issue)"
