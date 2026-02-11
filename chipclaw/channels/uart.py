"""
ChipClaw UART Channel
"""
import json

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from machine import UART
    UART_AVAILABLE = True
except ImportError:
    UART_AVAILABLE = False

from .base import BaseChannel
from ..bus.events import InboundMessage


class UARTChannel(BaseChannel):
    """UART serial communication channel"""
    
    def __init__(self, bus, config):
        super().__init__("uart", bus, config)
        self.uart = None
        self.buffer = ""
        self._running = False
    
    async def start(self):
        """Initialize UART and start reading"""
        if not UART_AVAILABLE:
            print("Warning: UART not available (not running on ESP32)")
            # For testing on desktop, we can skip UART
            return
        
        print(f"Starting UART channel: UART{self.config.get('uart_id', 1)} @ {self.config.get('baudrate', 115200)} baud")
        
        try:
            self.uart = UART(
                self.config.get("uart_id", 1),
                baudrate=self.config.get("baudrate", 115200),
                tx=self.config.get("tx_pin", 17),
                rx=self.config.get("rx_pin", 18)
            )
            
            print("UART initialized")
            
            # Start read loop
            self._running = True
            asyncio.create_task(self._read_loop())
        
        except Exception as e:
            print(f"Error starting UART channel: {e}")
    
    async def _read_loop(self):
        """Background loop to read UART data"""
        while self._running:
            try:
                if self.uart and self.uart.any():
                    # Read available data
                    chunk = self.uart.read()
                    if chunk:
                        self.buffer += chunk.decode('utf-8', errors='ignore')
                        
                        # Process complete lines
                        while '\n' in self.buffer:
                            line, self.buffer = self.buffer.split('\n', 1)
                            line = line.strip()
                            if line:
                                await self._handle_line(line)
                
                await asyncio.sleep_ms(50)
            
            except Exception as e:
                print(f"Error in UART read loop: {e}")
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
            
            # Create InboundMessage
            inbound = InboundMessage(
                channel="uart",
                sender_id=sender_id,
                chat_id=chat_id,
                content=content
            )
            
            await self.bus.publish_inbound(inbound)
        
        except Exception as e:
            print(f"Error handling UART line: {e}")
    
    async def send(self, msg):
        """Send OutboundMessage via UART"""
        if not self.uart:
            print("Error: UART not initialized")
            return
        
        try:
            # Send as JSON
            payload = json.dumps({
                "content": msg.content,
                "chat_id": msg.chat_id
            }) + '\n'
            
            self.uart.write(payload.encode('utf-8'))
            print(f"UART sent: {msg.content[:50]}...")
        
        except Exception as e:
            print(f"Error sending UART message: {e}")
    
    async def stop(self):
        """Stop UART channel"""
        self._running = False
        if self.uart:
            try:
                self.uart.deinit()
            except:
                pass
