---
name: peripheral_api
description: MicroPython peripheral API reference for ESP32-S3 (SPI, UART, Timer, NeoPixel, DHT, OneWire, etc.)
load: always
---

# MicroPython Peripheral API Reference

This skill provides usage examples for common ESP32-S3 MicroPython peripheral APIs.
Use `exec_micropython` to run these code snippets directly, or use `write_file` to create a `.py` file and then `exec_micropython` to import and run it.

## Execution Patterns

### Pattern 1: Direct exec/eval
```python
# Use exec_micropython tool to run code directly
exec_micropython(code="from machine import Pin; Pin(2, Pin.OUT).on(); print('LED on')")
```

### Pattern 2: Create .py file and import
```python
# Step 1: Use write_file to create a reusable module
write_file(path="my_sensor.py", content="""
from machine import Pin, SoftI2C
import time

class MySensor:
    def __init__(self, scl=22, sda=21, addr=0x48):
        self.i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self.addr = addr

    def read_temp(self):
        data = self.i2c.readfrom(self.addr, 2)
        return ((data[0] << 8) | data[1]) >> 4
""")

# Step 2: Use exec_micropython to import and run it
exec_micropython(code="import my_sensor; s = my_sensor.MySensor(); print(s.read_temp())")
```

## SPI Bus

### SPI Init and Transfer
```python
from machine import Pin, SPI

# Hardware SPI (id=1 or 2)
spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Write bytes
spi.write(b'\\x01\\x02')

# Read bytes
buf = bytearray(4)
spi.readinto(buf)

# Write and read simultaneously
tx = b'\\x00\\x00'
rx = bytearray(2)
spi.write_readinto(tx, rx)
print("SPI RX:", rx)
```

### SPI with Chip Select
```python
from machine import Pin, SPI

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT)

cs.off()  # Select device
spi.write(b'\\x9F')  # Send command
device_id = spi.read(3)  # Read response
cs.on()  # Deselect
print("Device ID:", device_id)
```

## Hardware UART

### UART Communication
```python
from machine import UART, Pin

# Initialize UART (id=1 or 2, not 0 which is REPL)
uart = UART(1, baudrate=9600, tx=Pin(17), rx=Pin(16))

# Write data
uart.write("Hello\\n")

# Read data (non-blocking)
if uart.any():
    data = uart.read()
    print("Received:", data)

# Read with timeout
data = uart.readline()  # Reads until newline or timeout
```

## Timer

### Periodic Timer
```python
from machine import Timer

def on_timer(t):
    print("Timer fired!")

# Create periodic timer (period in ms)
tim = Timer(0)
tim.init(period=1000, mode=Timer.PERIODIC, callback=on_timer)

# One-shot timer
tim2 = Timer(1)
tim2.init(period=5000, mode=Timer.ONE_SHOT, callback=on_timer)

# Stop timer
tim.deinit()
```

## NeoPixel (WS2812 / Addressable LEDs)

### NeoPixel Control
```python
from machine import Pin
from neopixel import NeoPixel

# Initialize: pin, number of LEDs
np = NeoPixel(Pin(48), 8)  # 8 LEDs on GPIO 48

# Set individual pixel (R, G, B)
np[0] = (255, 0, 0)    # Red
np[1] = (0, 255, 0)    # Green
np[2] = (0, 0, 255)    # Blue
np.write()              # Update LEDs

# Set all pixels
for i in range(8):
    np[i] = (10, 10, 10)  # Dim white
np.write()

# Turn off all
for i in range(8):
    np[i] = (0, 0, 0)
np.write()
```

## DHT Temperature/Humidity Sensor

### DHT11 / DHT22
```python
import dht
from machine import Pin

# DHT11
d = dht.DHT11(Pin(4))
d.measure()
print("Temperature:", d.temperature(), "C")
print("Humidity:", d.humidity(), "%")

# DHT22 (more precise)
d22 = dht.DHT22(Pin(4))
d22.measure()
print("Temperature:", d22.temperature(), "C")
print("Humidity:", d22.humidity(), "%")
```

## OneWire / DS18X20 Temperature Sensor

### DS18B20 Reading
```python
import onewire
import ds18x20
from machine import Pin
import time

ow = onewire.OneWire(Pin(4))
ds = ds18x20.DS18X20(ow)

# Scan for devices
roms = ds.scan()
print("Found devices:", roms)

# Read temperature
ds.convert_temp()
time.sleep_ms(750)  # Wait for conversion
for rom in roms:
    temp = ds.read_temp(rom)
    print("Temperature:", temp, "C")
```

## Servo Motor (via PWM)

### Servo Control
```python
from machine import Pin, PWM

servo = PWM(Pin(15), freq=50)  # 50Hz for servo

def set_angle(angle):
    # Map 0-180 degrees to duty 26-128 (0.5ms-2.5ms at 50Hz)
    duty = int(26 + (angle / 180) * 102)
    servo.duty(duty)

set_angle(0)    # 0 degrees
set_angle(90)   # 90 degrees (center)
set_angle(180)  # 180 degrees
```

## I2C Read/Write

### I2C Device Communication
```python
from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# Scan for devices
devices = i2c.scan()
print("I2C devices:", [hex(d) for d in devices])

# Write to device
i2c.writeto(0x48, b'\\x00')

# Read from device
data = i2c.readfrom(0x48, 2)
print("Read:", data)

# Write then read (register access)
i2c.writeto(0x48, b'\\x01')       # Set register
data = i2c.readfrom(0x48, 2)      # Read value
print("Register value:", data)

# Memory read/write (for EEPROM, etc.)
i2c.writeto_mem(0x50, 0x00, b'\\x42')   # Write to address 0x00
val = i2c.readfrom_mem(0x50, 0x00, 1)   # Read from address 0x00
```

## Deep Sleep and Wake

### Power Management
```python
import machine
import time

# Deep sleep for 10 seconds
print("Going to sleep...")
machine.deepsleep(10000)  # ms

# Configure wake-up from pin
from machine import Pin
wake_pin = Pin(0, Pin.IN, Pin.PULL_UP)
machine.wake_reason()  # Check why we woke up
```

## Watchdog Timer

### WDT
```python
from machine import WDT

# Enable watchdog (timeout in ms)
wdt = WDT(timeout=5000)

# Feed the watchdog (must call periodically)
wdt.feed()
```

## Notes

- Always call `deinit()` on PWM/Timer objects when done
- Use `SoftI2C` instead of `I2C` for flexible pin assignment
- UART 0 is reserved for REPL; use UART 1 or 2
- `gc.collect()` after heavy peripheral operations to free memory
- For complex drivers, create a `.py` file with `write_file` and import it via `exec_micropython`
