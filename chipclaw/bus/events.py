"""
ChipClaw Message Bus Events
"""


class InboundMessage:
    """Message from external channel to agent"""
    
    def __init__(self, channel, sender_id, chat_id, content, media=None, metadata=None):
        self.channel = channel        # Channel name (e.g., "mqtt", "uart")
        self.sender_id = sender_id    # Sender identifier
        self.chat_id = chat_id        # Conversation/chat identifier
        self.content = content        # Message text content
        self.media = media            # Optional media data
        self.metadata = metadata or {}  # Optional metadata dict
    
    @property
    def session_key(self):
        """Return session key for session management: 'channel:chat_id'"""
        return f"{self.channel}:{self.chat_id}"
    
    def __repr__(self):
        return f"InboundMessage(channel={self.channel}, sender_id={self.sender_id}, chat_id={self.chat_id}, content={self.content[:50]}...)"


class OutboundMessage:
    """Message from agent to external channel"""
    
    def __init__(self, channel, chat_id, content, reply_to=None, media=None, metadata=None):
        self.channel = channel        # Target channel name
        self.chat_id = chat_id        # Target conversation/chat
        self.content = content        # Message text content
        self.reply_to = reply_to      # Optional reference to InboundMessage
        self.media = media            # Optional media data
        self.metadata = metadata or {}  # Optional metadata dict
    
    def __repr__(self):
        return f"OutboundMessage(channel={self.channel}, chat_id={self.chat_id}, content={self.content[:50]}...)"
