"""
ChipClaw UART Channel
Reuses MicroPython REPL stdio (sys.stdin/sys.stdout) for input/output
"""
import sys
import json

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    import uselect as select
except ImportError:
    import select

from .base import BaseChannel
from ..bus.events import InboundMessage


class UARTChannel(BaseChannel):
    """UART channel using REPL stdio for communication"""
    
    def __init__(self, bus, config):
        super().__init__("uart", bus, config)
        self.buffer = ""
        self._running = False
        self._poller = None
    
    async def start(self):
        """Initialize stdio polling and start reading"""
        print("Starting UART channel (stdio mode)")
        
        try:
            self._poller = select.poll()
            self._poller.register(sys.stdin, select.POLLIN)
        except Exception as e:
            print("Warning: Could not setup stdin polling: {}".format(e))
            self._poller = None
        
        self._running = True
        asyncio.create_task(self._read_loop())
    
    async def _read_loop(self):
        """Background loop to read stdin data"""
        while self._running:
            try:
                if self._poller:
                    events = self._poller.poll(0)
                    for _, ev in events:
                        if ev & select.POLLIN:
                            ch = sys.stdin.read(1)
                            if ch:
                                self.buffer += ch
                    
                    # Process complete lines
                    while '\n' in self.buffer:
                        line, self.buffer = self.buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            await self._handle_line(line)
                
                await asyncio.sleep_ms(50)
            
            except Exception as e:
                print("Error in UART read loop: {}".format(e))
                await asyncio.sleep(1)
    
    async def _handle_line(self, line):
        """Parse line (JSON or plain text) and create InboundMessage"""
        try:
            # Try to parse as JSON
            try:
                data = json.loads(line)
                content = data.get("content", line)
                sender_id = data.get("sender_id", "uart_user")
                chat_id = data.get("chat_id", "uart_default")
            except:
                # Plain text
                content = line
                sender_id = "uart_user"
                chat_id = "uart_default"
            
            inbound = InboundMessage(
                channel="uart",
                sender_id=sender_id,
                chat_id=chat_id,
                content=content
            )
            
            await self.bus.publish_inbound(inbound)
        
        except Exception as e:
            print("Error handling UART line: {}".format(e))
    
    async def send(self, msg):
        """Send OutboundMessage via stdout"""
        try:
            payload = json.dumps({
                "content": msg.content,
                "chat_id": msg.chat_id
            })
            sys.stdout.write(payload + '\n')
        
        except Exception as e:
            print("Error sending UART message: {}".format(e))
    
    async def stop(self):
        """Stop UART channel"""
        self._running = False
        if self._poller:
            try:
                self._poller.unregister(sys.stdin)
            except:
                pass
