"""
ChipClaw Hardware Tools
GPIO, I2C, PWM, ADC control for ESP32-S3
"""
from .base import Tool

try:
    from machine import Pin, PWM, ADC, SoftI2C
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False


class GPIOTool(Tool):
    """GPIO operations: read, write, pwm, adc"""
    
    name = "gpio"
    description = "Control GPIO pins (modes: read, write, pwm, adc)"
    parameters = {
        "type": "object",
        "properties": {
            "pin": {
                "type": "integer",
                "description": "GPIO pin number"
            },
            "mode": {
                "type": "string",
                "enum": ["read", "write", "pwm", "adc"],
                "description": "Operation mode"
            },
            "value": {
                "type": "integer",
                "description": "Value for write mode (0 or 1) or PWM duty cycle (0-1023)"
            },
            "freq": {
                "type": "integer",
                "description": "PWM frequency in Hz (default: 1000)"
            }
        },
        "required": ["pin", "mode"]
    }
    
    def execute(self, pin, mode, value=None, freq=1000):
        """Execute GPIO operation"""
        if not HARDWARE_AVAILABLE:
            return "Error: Hardware not available (not running on ESP32)"
        
        try:
            if mode == "read":
                p = Pin(pin, Pin.IN)
                return f"GPIO {pin} = {p.value()}"
            
            elif mode == "write":
                if value is None:
                    return "Error: 'value' parameter required for write mode"
                p = Pin(pin, Pin.OUT)
                p.value(value)
                return f"GPIO {pin} set to {value}"
            
            elif mode == "pwm":
                if value is None:
                    return "Error: 'value' parameter required for PWM mode (duty cycle 0-1023)"
                pwm = PWM(Pin(pin), freq=freq)
                pwm.duty(value)
                return f"PWM on GPIO {pin}: freq={freq}Hz, duty={value}"
            
            elif mode == "adc":
                adc = ADC(Pin(pin))
                # ESP32 ADC attenuation: 0-3.3V range
                adc.atten(ADC.ATTN_11DB)
                reading = adc.read()
                voltage = reading * 3.3 / 4095
                return f"ADC on GPIO {pin}: raw={reading}, voltage={voltage:.3f}V"
            
            else:
                return f"Error: Unknown mode '{mode}'"
        
        except Exception as e:
            return f"Error: {e}"


class I2CScanTool(Tool):
    """Scan I2C bus for devices"""
    
    name = "i2c_scan"
    description = "Scan I2C bus and return list of detected device addresses"
    parameters = {
        "type": "object",
        "properties": {
            "scl": {
                "type": "integer",
                "description": "SCL pin number (default: 22)"
            },
            "sda": {
                "type": "integer",
                "description": "SDA pin number (default: 21)"
            }
        }
    }
    
    def execute(self, scl=22, sda=21):
        """Scan I2C bus"""
        if not HARDWARE_AVAILABLE:
            return "Error: Hardware not available (not running on ESP32)"
        
        try:
            i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
            devices = i2c.scan()
            
            if devices:
                addr_list = [f"0x{addr:02x}" for addr in devices]
                return f"I2C devices found: {', '.join(addr_list)}"
            else:
                return "No I2C devices found"
        
        except Exception as e:
            return f"Error: {e}"
