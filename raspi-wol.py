import RPi.GPIO as GPIO
import time
import socket
import struct
import sys
import logging
import subprocess
import os

# Configuration
RELAY_PIN = 24     # Pin connected to the relay
LED_PIN = 23       # Pin connected to the LED
PING_INTERVAL = 1  # Interval in seconds between pings

if len(sys.argv) != 3:
    print("Usage: python raspi-wol.py <MAC_ADDRESS> <PING_IP>")
    sys.exit(1)

MAC_ADDRESS = sys.argv[1]
PING_IP = sys.argv[2]

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)

PID_FILE = f"/run/raspi-wol/raspi-wol-{os.getpid()}.pid"
PID_DIR = "/run/raspi-wol"

def create_pid_directory():
    """Create the PID directory if it does not exist."""
    if not os.path.exists(PID_DIR):
        os.makedirs(PID_DIR, exist_ok=True)
        logging.info(f"PID directory {PID_DIR} created")

def create_pid_file():
    """Create a PID file to store the process ID."""
    create_pid_directory()
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    logging.info(f"PID file created at {PID_FILE} with PID {pid}")

def remove_pid_file():
    """Remove the PID file."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logging.info(f"PID file {PID_FILE} removed")

def send_wol_packet(mac_address):
    logging.info(f"Sending WOL packet to MAC address: {mac_address}")
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
    logging.info("WOL packet sent successfully")

def is_host_reachable(ip):
    """Ping the given IP address and return True if reachable, False otherwise."""
    try:
        subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def log_debug_info():
    """Log debug information for systemd troubleshooting."""
    logging.info(f"Script executed with PID: {os.getpid()}")
    logging.info(f"MAC_ADDRESS: {MAC_ADDRESS}, PING_IP: {PING_IP}")
    logging.info(f"PID_FILE: {PID_FILE}")
    logging.info(f"GPIO mode: {GPIO.getmode()}, RELAY_PIN: {RELAY_PIN}, LED_PIN: {LED_PIN}")

try:
    log_debug_info()
    create_pid_file()
    logging.info("Script started, monitoring relay state and pinging IP")
    relay_state = GPIO.input(RELAY_PIN)
    led_on = False  # Track LED state
    while True:
        # Monitor relay state
        current_state = GPIO.input(RELAY_PIN)
        if current_state == GPIO.HIGH and relay_state == GPIO.LOW:
            logging.info("Relay turned on")
            send_wol_packet(MAC_ADDRESS)
        relay_state = current_state

        # Ping IP and control LED
        if is_host_reachable(PING_IP):
            if not led_on:
                GPIO.output(LED_PIN, GPIO.HIGH)
                logging.info(f"Host {PING_IP} is reachable, LED turned on")
                led_on = True
        else:
            if led_on:
                GPIO.output(LED_PIN, GPIO.LOW)
                logging.info(f"Host {PING_IP} is unreachable, LED turned off")
                led_on = False

        time.sleep(PING_INTERVAL)  # Polling interval
except KeyboardInterrupt:
    logging.info("Script interrupted by user")
finally:
    GPIO.cleanup()
    remove_pid_file()
    logging.info("GPIO cleanup done")
