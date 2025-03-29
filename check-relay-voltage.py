import RPi.GPIO as GPIO
import time
import os
import sys
from wakeonlan import send_magic_packet

# Configure GPIO settings
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setwarnings(False)

# Define the GPIO pins
RELAY_PIN = 24  # Change this to the GPIO pin you are using
LED_PIN = 23    # GPIO pin for the LED

# Set up the GPIO pins
GPIO.setup(RELAY_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED is off initially

def ping_ip(ip_address):
    """Ping the specified IP address and return True if reachable."""
    response = os.system(f"ping -c 1 {ip_address} > /dev/null 2>&1")
    return response == 0

def wake_on_lan(mac_address):
    """Send a magic packet to wake up a device with the specified MAC address."""
    try:
        send_magic_packet(mac_address)
        print(f"Magic packet sent to {mac_address}")
    except Exception as e:
        print(f"Failed to send magic packet: {e}")

def check_voltage_and_ping(ip_address):
    try:
        while True:
            # Check relay voltage
            voltage_state = GPIO.input(RELAY_PIN)
            if voltage_state == GPIO.HIGH:
                print("Relay voltage detected: HIGH")
            else:
                print("Relay voltage detected: LOW")

            # Ping the IP address
            if ping_ip(ip_address):
                print(f"Ping to {ip_address} successful. Turning LED ON.")
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                print(f"Ping to {ip_address} failed. Turning LED OFF.")
                GPIO.output(LED_PIN, GPIO.LOW)

            time.sleep(1)  # Delay for 1 second
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check-relay-voltage.py <IP_ADDRESS> [MAC_ADDRESS]")
        sys.exit(1)

    ip_address = sys.argv[1]
    mac_address = sys.argv[2] if len(sys.argv) > 2 else None

    if mac_address:
        wake_on_lan(mac_address)

    check_voltage_and_ping(ip_address)
