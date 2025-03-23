import RPi.GPIO as GPIO
import time
import socket
import struct
import sys

# Configuration
POWER_SWITCH_PIN = 4
LED_PIN = 14
if len(sys.argv) != 2:
    print("Usage: python raspi-wol.py <MAC_ADDRESS>")
    sys.exit(1)

MAC_ADDRESS = sys.argv[1]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)

def send_wol_packet(mac_address):
    # Construct the Wake-on-LAN "Magic Packet"
    mac_address = mac_address.replace(':', '')
    data = 'FF' * 6 + mac_address * 16
    send_data = b''

    for i in range(0, len(data), 2):
        send_data += struct.pack('B', int(data[i:i + 2], 16))

    # Send the packet to the broadcast address using UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 9))
    sock.close()

def power_switch_callback(channel):
    GPIO.output(LED_PIN, GPIO.HIGH)
    send_wol_packet(MAC_ADDRESS)
    time.sleep(1)  # Keep the LED on for 1 second
    GPIO.output(LED_PIN, GPIO.LOW)

# Add event detection for the power switch
GPIO.add_event_detect(POWER_SWITCH_PIN, GPIO.RISING, callback=power_switch_callback, bouncetime=300)

try:
    # Keep the script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
