"""
ChipClaw MQTT Channel
"""
import json

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from umqtt.robust import MQTTClient
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

from .base import BaseChannel
from ..bus.events import InboundMessage


class MQTTChannel(BaseChannel):
    """MQTT communication channel"""
    
    def __init__(self, bus, config):
        super().__init__("mqtt", bus, config)
        self.client = None
        self.topic_in = config.get("topic_in", "chipclaw/in")
        self.topic_out = config.get("topic_out", "chipclaw/out")
        self._running = False
    
    async def start(self):
        """Connect to MQTT broker and start listening"""
        if not MQTT_AVAILABLE:
            print("Error: MQTT not available (umqtt not installed)")
            return
        
        print(f"Starting MQTT channel: {self.config.get('broker')}:{self.config.get('port')}")
        
        try:
            self.client = MQTTClient(
                client_id=self.config.get("client_id", "chipclaw-01"),
                server=self.config.get("broker", "localhost"),
                port=self.config.get("port", 1883),
                user=self.config.get("username") or None,
                password=self.config.get("password") or None
            )
            
            # Set callback for incoming messages
            self.client.set_callback(self._on_message)
            
            # Connect and subscribe
            self.client.connect()
            self.client.subscribe(self.topic_in)
            
            print(f"MQTT connected, subscribed to {self.topic_in}")
            
            # Start poll loop
            self._running = True
            asyncio.create_task(self._poll_loop())
        
        except Exception as e:
            print(f"Error starting MQTT channel: {e}")
    
    def _on_message(self, topic, msg):
        """
        MQTT message callback
        Note: This is synchronous, need to schedule async task
        """
        try:
            # Parse JSON message
            data = json.loads(msg.decode())
            
            # Create InboundMessage
            inbound = InboundMessage(
                channel="mqtt",
                sender_id=data.get("sender_id", "unknown"),
                chat_id=data.get("chat_id", topic.decode()),
                content=data.get("content", "")
            )
            
            # Schedule publish to bus
            asyncio.create_task(self.bus.publish_inbound(inbound))
        
        except Exception as e:
            print(f"Error parsing MQTT message: {e}")
    
    async def _poll_loop(self):
        """Background loop to check for MQTT messages"""
        while self._running:
            try:
                if self.client:
                    # Check for messages (non-blocking)
                    self.client.check_msg()
                await asyncio.sleep_ms(100)
            except Exception as e:
                print(f"Error in MQTT poll loop: {e}")
                # Try to reconnect
                await asyncio.sleep(5)
                try:
                    self.client.connect()
                    self.client.subscribe(self.topic_in)
                except:
                    pass
    
    async def send(self, msg):
        """Send OutboundMessage via MQTT"""
        if not self.client:
            print("Error: MQTT client not connected")
            return
        
        try:
            payload = json.dumps({
                "content": msg.content,
                "chat_id": msg.chat_id
            })
            self.client.publish(self.topic_out, payload)
            print(f"MQTT sent to {self.topic_out}")
        
        except Exception as e:
            print(f"Error sending MQTT message: {e}")
    
    async def stop(self):
        """Stop MQTT channel"""
        self._running = False
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
