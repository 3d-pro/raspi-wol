import RPi.GPIO as GPIO
import time, socket, struct, sys, logging, subprocess, os, signal, atexit

# Configuration
RELAY_PIN           = 24 # Pin connected to the relay
LED_PIN             = 23 # Pin connected to the LED
POLLING_INTERVAL    = 1  # Polling interval in seconds
PING_FAIL_THRESHOLD = 3  # Number of failed pings before turning off the LED

if len(sys.argv) != 2:
    print("Usage: python raspi-wol.py <MAC_ADDRESS_IP>")
    sys.exit(1)

# Parse the combined argument
try:
    mac_ip = sys.argv[1]
    MAC_ADDRESS, PING_IP = mac_ip.split('_')
except ValueError:
    print("Error: Argument must be in the format <MAC_ADDRESS>_<PING_IP>")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)

PID_FILE = f"/run/raspi-wol/raspi-wol-{os.getpid()}.pid"

def create_pid_file():
    """Create a PID file to store the process ID."""
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))

def remove_pid_file():
    """Remove the PID file."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def send_wol_packet(mac_address):
    logging.warning(f"Sending WOL packet to MAC address: {mac_address}")
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

def is_host_reachable(ip):
    """Ping the given IP address and return True if reachable, False otherwise."""
    try:
        subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def log_debug_info():
    """Log essential debug information for systemd troubleshooting."""
    logging.warning(f"Script executed with PID: {os.getpid()}")
    logging.warning(f"MAC_ADDRESS: {MAC_ADDRESS}, PING_IP: {PING_IP}")
    logging.warning(f"PID_FILE: {PID_FILE}")
    logging.warning(f"GPIO mode: {GPIO.getmode()}, RELAY_PIN: {RELAY_PIN}, LED_PIN: {LED_PIN}")

def cleanup():
    """Perform cleanup tasks such as GPIO cleanup and removing the PID file."""
    GPIO.cleanup()
    remove_pid_file()

def handle_exit_signal(signum, frame):
    """Handle termination signals to clean up resources."""
    cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, handle_exit_signal)
signal.signal(signal.SIGINT, handle_exit_signal)

# Register cleanup function with atexit
atexit.register(cleanup)

try:
    log_debug_info()
    create_pid_file()
    logging.warning("Script started, monitoring relay state and pinging IP")
    relay_state = GPIO.input(RELAY_PIN)
    led_on = False  # Track LED state
    failed_pings = 0  # Track consecutive failed pings

    while True:
        # Monitor relay state
        current_state = GPIO.input(RELAY_PIN)
        if current_state == GPIO.HIGH and relay_state == GPIO.LOW:
            logging.warning("Relay turned on")
            send_wol_packet(MAC_ADDRESS)
        relay_state = current_state

        # Ping IP and control LED
        if is_host_reachable(PING_IP):
            failed_pings = 0
            if not led_on:
                GPIO.output(LED_PIN, GPIO.HIGH)
                logging.warning(f"Host {PING_IP} is reachable, LED turned on")
                led_on = True
        else:
            failed_pings += 1
            if failed_pings >= PING_FAIL_THRESHOLD and led_on:
                GPIO.output(LED_PIN, GPIO.LOW)
                logging.warning(f"Host {PING_IP} is unreachable after {PING_FAIL_THRESHOLD} failed pings, LED turned off")
                led_on = False

        time.sleep(POLLING_INTERVAL)  # Polling interval
except KeyboardInterrupt:
    pass
finally:
    cleanup()
