"""
ChipClaw Boot Script
Initializes WiFi and NTP before main.py
"""
import time
import json

try:
    import network
    import ntptime
    MICROPYTHON = True
except ImportError:
    MICROPYTHON = False
    print("Running in CPython mode - skipping WiFi/NTP")

if MICROPYTHON:
    # Load config
    try:
        with open("/config.json") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        config = {"wifi": {"ssid": "", "password": ""}}
    
    wifi_config = config.get("wifi", {})
    ssid = wifi_config.get("ssid", "")
    password = wifi_config.get("password", "")
    
    if ssid:
        # Connect WiFi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f"Connecting to WiFi '{ssid}'...")
            wlan.connect(ssid, password)
            
            # Wait for connection (timeout 10 seconds)
            timeout = 10
            start = time.time()
            while not wlan.isconnected() and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if wlan.isconnected():
                print("WiFi connected:", wlan.ifconfig()[0])
                
                # Sync NTP
                try:
                    ntptime.settime()
                    print("NTP time synced")
                except Exception as e:
                    print(f"NTP sync failed: {e}")
            else:
                print("WiFi connection timeout")
        else:
            print("WiFi already connected:", wlan.ifconfig()[0])
    else:
        print("No WiFi credentials configured")
