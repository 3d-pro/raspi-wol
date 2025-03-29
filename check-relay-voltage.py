import RPi.GPIO as GPIO
import time

# Configure GPIO settings
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setwarnings(False)

# Define the GPIO pin to check
RELAY_PIN = 2  # Change this to the GPIO pin you are using

# Set up the GPIO pin as an input
GPIO.setup(RELAY_PIN, GPIO.IN)

def check_voltage():
    try:
        while True:
            # Read the voltage state of the relay pin
            voltage_state = GPIO.input(RELAY_PIN)
            if voltage_state == GPIO.HIGH:
                print("Relay voltage detected: HIGH")
            else:
                print("Relay voltage detected: LOW")
            time.sleep(1)  # Delay for 1 second
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == "__main__":
    check_voltage()
