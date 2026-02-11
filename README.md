# ChipClaw

**ChipClaw** is a lightweight AI agent framework for ESP32-S3 microcontrollers, porting the core architecture of [HKUDS/nanobot](https://github.com/HKUDS/nanobot) to MicroPython. It enables autonomous hardware control, self-programming capabilities, and multi-channel communication through MQTT and UART interfaces.

## Features

- 🤖 **Autonomous AI Agent**: LLM-powered decision making and task execution
- ⚡ **ESP32-S3 Optimized**: Runs on 16MB Flash / 8MB PSRAM
- 🔌 **Multi-Channel I/O**: MQTT (wireless) and UART (serial) communication
- 🛠️ **Rich Tool System**: Filesystem, hardware control, HTTP fetch, self-programming
- 🧠 **Memory System**: Long-term memory and daily notes
- 📚 **Skills Framework**: Markdown-based skill documents
- 🔧 **Hardware Control**: GPIO, I2C, PWM, ADC interfaces
- 💻 **Self-Programming**: Execute MicroPython code via `exec()`

## Hardware Requirements

- **Microcontroller**: ESP32-S3 (16MB Flash, 8MB PSRAM)
- **Firmware**: MicroPython v1.20 or later
- **Network**: WiFi for LLM API access and MQTT
- **Optional**: UART cable for serial communication

## Quick Start

### 1. Flash MicroPython Firmware

Download and flash the ESP32-S3 MicroPython firmware:

```bash
esptool.py --chip esp32s3 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32s3 --port /dev/ttyUSB0 write_flash -z 0x0 esp32s3-firmware.bin
```

### 2. Configure WiFi and API

Edit `config.json`:

```json
{
  "provider": {
    "api_key": "your-api-key-here",
    "api_base": "https://api.deepseek.com/v1"
  },
  "wifi": {
    "ssid": "your-wifi-ssid",
    "password": "your-wifi-password"
  }
}
```

### 3. Upload Files to ESP32

Use `ampy`, `rshell`, or Thonny IDE to upload the entire repository to your ESP32-S3:

```bash
# Using ampy
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.json
ampy --port /dev/ttyUSB0 put chipclaw
ampy --port /dev/ttyUSB0 put workspace
ampy --port /dev/ttyUSB0 put data
```

### 4. Run ChipClaw

Reset your ESP32-S3 or run:

```bash
# Connect to REPL
screen /dev/ttyUSB0 115200

# In MicroPython REPL:
>>> import main
```

ChipClaw will start and listen on UART by default. Send messages and interact!

## Architecture

ChipClaw mirrors nanobot's architecture while adapting for embedded constraints:

- **Message Bus**: `uasyncio.Queue`-based event routing
- **LLM Provider**: OpenAI-compatible API via `urequests`
- **Agent Loop**: Message → LLM → Tools → Response cycle
- **Context Builder**: System prompt from bootstrap + memory + skills
- **Memory System**: MEMORY.md + daily notes (YYYY-MM-DD.md)
- **Skills Loader**: Frontmatter-parsed markdown documents
- **Tool Registry**: Filesystem, hardware, exec, HTTP fetch, messaging
- **Channels**: MQTT (wireless), UART (serial)
- **Session Manager**: JSONL conversation history

See [docs/DESIGN.md](docs/DESIGN.md) for the complete architecture design document.

## Directory Structure

```
/
├── boot.py                    # WiFi + NTP initialization
├── main.py                    # Entry point
├── config.json                # Configuration
├── chipclaw/                  # Main package
│   ├── config.py              # Config loader
│   ├── utils.py               # Utilities
│   ├── bus/                   # Message bus
│   ├── providers/             # LLM providers
│   ├── agent/                 # Agent core
│   │   ├── loop.py            # Main loop
│   │   ├── context.py         # Context builder
│   │   ├── memory.py          # Memory system
│   │   ├── skills.py          # Skills loader
│   │   └── tools/             # Tool implementations
│   ├── channels/              # Communication channels
│   └── session/               # Session management
├── workspace/                 # User workspace
│   ├── IDENTITY.md            # Agent identity
│   ├── AGENTS.md              # Behavior guidelines
│   ├── memory/                # Memory storage
│   └── skills/                # Skills library
└── data/                      # Runtime data
    └── sessions/              # Conversation history
```

## Example Interaction

```
User: Turn on the LED on pin 2

ChipClaw: I'll turn on the LED for you.
[Executes: gpio(pin=2, mode="write", value=1)]
LED on GPIO pin 2 has been turned on.

User: Read the temperature sensor on I2C address 0x48

ChipClaw: Let me scan the I2C bus first to confirm the device.
[Executes: i2c_scan(scl=22, sda=21)]
I found a device at 0x48. Now I'll write code to read it.
[Executes: exec_micropython(...)]
Temperature: 24.5°C
```

## Configuration

Key configuration options in `config.json`:

- `agent.model`: LLM model name (default: "deepseek-chat")
- `agent.max_tokens`: Maximum tokens per response (default: 4096)
- `agent.workspace`: Workspace directory (default: "/workspace")
- `provider.api_key`: LLM API key
- `provider.api_base`: API endpoint URL
- `channels.mqtt.enabled`: Enable MQTT channel
- `channels.uart.enabled`: Enable UART channel (default: true)
- `hardware.restrict_to_workspace`: Limit file access to workspace

## Tools Available

ChipClaw provides the following tools to the LLM:

1. **read_file** - Read file contents
2. **write_file** - Write file contents
3. **list_dir** - List directory contents
4. **gpio** - GPIO operations (read, write, pwm, adc)
5. **i2c_scan** - Scan I2C bus for devices
6. **exec_micropython** - Execute MicroPython code
7. **http_fetch** - HTTP GET requests
8. **send_message** - Send messages to channels

## Memory Management

ChipClaw is designed for 8MB PSRAM:

- Session history limited to 20 messages
- HTTP responses truncated to 4KB
- File reads truncated to 10KB
- `gc.collect()` after major operations
- 3-day memory window (vs. 7 in nanobot)

## Safety Considerations

⚠️ **Important**: ChipClaw uses `exec()` for self-programming, which is intentionally unrestricted. This is a feature, not a bug - it enables autonomous hardware control. However:

- The agent has full control over your ESP32
- It can execute any MicroPython code
- Always review the agent's actions
- Have a recovery mechanism (UART bootloader)
- Use in trusted environments only

## Development

### Testing on Desktop

ChipClaw includes fallbacks for desktop Python testing:

```bash
# Install dependencies
pip install aiohttp

# Run main.py (will use fallbacks for MicroPython modules)
python main.py
```

### Resource Analysis

- **Flash Usage**: ~100KB for ChipClaw code
- **Peak RAM**: ~450KB (including TLS handshake)
- **Available for data**: ~13.5MB Flash, ~7.5MB PSRAM

## Roadmap

Future enhancements (not in current scope):

- [ ] OTA updates
- [ ] Local LLM inference
- [ ] Voice I/O (I2S)
- [ ] Camera support
- [ ] BLE channel
- [ ] Web UI
- [ ] Multi-agent collaboration

## License

[Add your license here]

## Credits

ChipClaw is inspired by and ports core concepts from [HKUDS/nanobot](https://github.com/HKUDS/nanobot).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- 📖 [Design Document](docs/DESIGN.md)
- 🐛 [Issue Tracker](https://github.com/0x1abin/chipclaw/issues)
- 💬 [Discussions](https://github.com/0x1abin/chipclaw/discussions)
