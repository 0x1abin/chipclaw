"""
ChipClaw Message Bus Queue
"""
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


# Simple asyncio Queue implementation for MicroPython
class Queue:
    """
    Simple async queue for MicroPython compatibility
    Mimics asyncio.Queue interface
    """
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._queue = []
        self._getters = []
        self._putters = []
    
    def qsize(self):
        """Return the size of the queue"""
        return len(self._queue)
    
    def empty(self):
        """Return True if the queue is empty"""
        return len(self._queue) == 0
    
    def full(self):
        """Return True if the queue is full"""
        return self.maxsize > 0 and len(self._queue) >= self.maxsize
    
    async def put(self, item):
        """Put an item into the queue"""
        # If queue is full and maxsize is set, wait
        while self.full():
            event = asyncio.Event()
            self._putters.append(event)
            await event.wait()
        
        self._queue.append(item)
        
        # Wake up a getter if any
        if self._getters:
            event = self._getters.pop(0)
            event.set()
    
    def put_nowait(self, item):
        """Put an item without blocking"""
        if self.full():
            raise Exception("Queue is full")
        self._queue.append(item)
        
        # Wake up a getter if any
        if self._getters:
            event = self._getters.pop(0)
            event.set()
    
    async def get(self):
        """Get an item from the queue"""
        # If queue is empty, wait for an item
        while self.empty():
            event = asyncio.Event()
            self._getters.append(event)
            await event.wait()
        
        item = self._queue.pop(0)
        
        # Wake up a putter if any
        if self._putters:
            event = self._putters.pop(0)
            event.set()
        
        return item
    
    def get_nowait(self):
        """Get an item without blocking"""
        if self.empty():
            raise Exception("Queue is empty")
        item = self._queue.pop(0)
        
        # Wake up a putter if any
        if self._putters:
            event = self._putters.pop(0)
            event.set()
        
        return item


class MessageBus:
    """Central message routing with asyncio queues"""
    
    def __init__(self):
        self.inbound = Queue()    # InboundMessage queue
        self.outbound = Queue()   # OutboundMessage queue
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
