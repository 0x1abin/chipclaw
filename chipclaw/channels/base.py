"""
ChipClaw Base Channel
"""


class BaseChannel:
    """Base class for communication channels"""
    
    def __init__(self, name, bus, config):
        self.name = name
        self.bus = bus
        self.config = config
    
    async def start(self):
        """
        Initialize and start the channel
        Override in subclass
        """
        raise NotImplementedError("Subclass must implement start()")
    
    async def stop(self):
        """
        Stop and cleanup the channel
        Override in subclass
        """
        raise NotImplementedError("Subclass must implement stop()")
    
    async def send(self, msg):
        """
        Send OutboundMessage
        Override in subclass
        
        Args:
            msg: OutboundMessage instance
        """
        raise NotImplementedError("Subclass must implement send()")
    
    def is_allowed(self, sender_id):
        """
        Check if sender is authorized
        Can be overridden for whitelist/blacklist
        
        Args:
            sender_id: Sender identifier
        
        Returns:
            Boolean
        """
        # Default: allow all
        return True
