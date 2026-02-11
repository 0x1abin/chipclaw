---
name: hardware_control
description: ESP32-S3 hardware control via GPIO, I2C, PWM, and ADC
load: always
---

# Hardware Control Skill

This skill provides comprehensive hardware control capabilities for the ESP32-S3.

## GPIO Operations

### Digital Read
Read the state of a digital input pin:
```json
{"name": "gpio", "params": {"pin": 34, "mode": "read"}}
```

### Digital Write
Set a digital output pin to HIGH (1) or LOW (0):
```json
{"name": "gpio", "params": {"pin": 2, "mode": "write", "value": 1}}
{"name": "gpio", "params": {"pin": 2, "mode": "write", "value": 0}}
```

### PWM (Pulse Width Modulation)
Control analog-like output for LEDs, motors, etc.:
```json
{"name": "gpio", "params": {"pin": 5, "mode": "pwm", "value": 512, "freq": 1000}}
```
- `value`: Duty cycle (0-1023)
- `freq`: Frequency in Hz (default: 1000)

### ADC (Analog to Digital Conversion)
Read analog voltage from a pin:
```json
{"name": "gpio", "params": {"pin": 34, "mode": "adc"}}
```
- Returns raw value (0-4095) and voltage (0-3.3V)
- Use pins 32-39 for ADC on ESP32-S3

## I2C Bus Scanning

Scan the I2C bus for connected devices:
```json
{"name": "i2c_scan", "params": {"scl": 22, "sda": 21}}
```
- Default pins: SCL=22, SDA=21
- Returns list of detected I2C addresses in hex format

## Common Use Cases

### LED Control
```python
# Turn on built-in LED (pin 2)
gpio(pin=2, mode="write", value=1)

# PWM dimming (50% brightness)
gpio(pin=2, mode="pwm", value=512)
```

### Sensor Reading
```python
# Read analog sensor on pin 34
gpio(pin=34, mode="adc")

# Scan for I2C sensors
i2c_scan(scl=22, sda=21)
```

### Motor Control
```python
# PWM motor speed control (75% speed)
gpio(pin=5, mode="pwm", value=768, freq=1000)
```

## Pin Reference (ESP32-S3)

- **GPIO 2**: Built-in LED (OUTPUT)
- **GPIO 32-39**: ADC capable (INPUT)
- **GPIO 21, 22**: Default I2C (SDA, SCL)
- **GPIO 0-21, 32-39**: General purpose I/O

## Safety Notes

1. Always verify pin numbers before operations
2. Some pins have special functions at boot - avoid GPIO 0, 2, 12, 15
3. Maximum GPIO current: 40mA per pin
4. Use external drivers for high-power devices
5. Never connect outputs directly together
