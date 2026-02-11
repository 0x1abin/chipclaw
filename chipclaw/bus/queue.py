"""
ChipClaw Message Bus Queue
"""
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class MessageBus:
    """Central message routing with asyncio queues"""
    
    def __init__(self):
        self.inbound = asyncio.Queue()    # InboundMessage queue
        self.outbound = asyncio.Queue()   # OutboundMessage queue
        self.subscribers = {}             # {channel_name: callback}
        self._running = False
    
    async def publish_inbound(self, msg):
        """
        Publish inbound message (Channel → Bus)
        
        Args:
            msg: InboundMessage instance
        """
        await self.inbound.put(msg)
    
    async def consume_inbound(self):
        """
        Consume inbound message (Bus → Agent)
        Blocks until message is available
        
        Returns:
            InboundMessage instance
        """
        return await self.inbound.get()
    
    async def publish_outbound(self, msg):
        """
        Publish outbound message (Agent → Bus)
        
        Args:
            msg: OutboundMessage instance
        """
        await self.outbound.put(msg)
    
    def subscribe_outbound(self, channel, callback):
        """
        Register channel callback for outbound dispatch
        
        Args:
            channel: Channel name (string)
            callback: Async function(OutboundMessage) -> None
        """
        self.subscribers[channel] = callback
    
    async def dispatch_outbound(self):
        """
        Background loop: dispatch outbound messages to channels
        Runs continuously until stop() is called
        """
        self._running = True
        while self._running:
            try:
                msg = await self.outbound.get()
                callback = self.subscribers.get(msg.channel)
                if callback:
                    try:
                        await callback(msg)
                    except Exception as e:
                        print(f"Error dispatching to {msg.channel}: {e}")
                else:
                    print(f"Warning: No subscriber for channel '{msg.channel}'")
            except Exception as e:
                print(f"Error in dispatch_outbound: {e}")
                if self._running:
                    await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the dispatch loop"""
        self._running = False
