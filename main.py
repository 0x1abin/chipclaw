"""
ChipClaw Main Entry Point
Initializes and runs the agent with all channels
"""
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from chipclaw.config import Config
from chipclaw.bus.queue import MessageBus
from chipclaw.providers.http_provider import HTTPProvider
from chipclaw.session.manager import SessionManager
from chipclaw.agent.loop import AgentLoop
from chipclaw.channels.mqtt import MQTTChannel
from chipclaw.channels.uart import UARTChannel


async def main():
    """Main async entry point"""
    print("=" * 50)
    print("ChipClaw - ESP32-S3 AI Agent")
    print("=" * 50)
    
    # Load configuration
    print("Loading configuration...")
    config = Config()
    
    # Initialize message bus
    print("Initializing message bus...")
    bus = MessageBus()
    
    # Initialize LLM provider
    print("Initializing LLM provider...")
    provider = HTTPProvider(
        api_key=config.get("provider", "api_key"),
        api_base=config.get("provider", "api_base")
    )
    
    # Initialize session manager
    print("Initializing session manager...")
    sessions = SessionManager(config.data_dir)
    
    # Initialize agent
    print("Initializing agent...")
    agent = AgentLoop(bus, provider, sessions, config)
    
    # Initialize channels
    channels = []
    
    # MQTT channel
    if config.get("channels", "mqtt", "enabled"):
        print("Initializing MQTT channel...")
        mqtt = MQTTChannel(bus, config.get("channels", "mqtt"))
        channels.append(mqtt)
        bus.subscribe_outbound("mqtt", mqtt.send)
    
    # UART channel
    if config.get("channels", "uart", "enabled"):
        print("Initializing UART channel...")
        uart = UARTChannel(bus, config.get("channels", "uart"))
        channels.append(uart)
        bus.subscribe_outbound("uart", uart.send)
    
    print(f"Initialized {len(channels)} channel(s)")
    
    # Gather all tasks
    print("Starting tasks...")
    tasks = [
        agent.run(),
        bus.dispatch_outbound()
    ]
    
    # Add channel tasks
    for ch in channels:
        tasks.append(ch.start())
    
    print("=" * 50)
    print("ChipClaw is running!")
    print("=" * 50)
    
    # Run all tasks
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Run the event loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import sys
        sys.print_exception(e)
