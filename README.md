# Raspberry Pi Wake-on-LAN (WOL) Service

This project allows you to use a Raspberry Pi to send Wake-on-LAN (WOL) packets to a device when a relay is triggered. It also monitors the device's availability via ping and controls an LED to indicate its status.

## Prerequisites

- Raspberry Pi with GPIO pins (Example in Raspberry Pi Zero 2W)
- Relay module (e.g., PC power switch) and LED connected to the specified GPIO pins
- Python 3 installed on the Raspberry Pi
- Systemd installed for managing the service

## Hardware Setup

This project uses a PC power switch as a relay since it acts like a relay. Below are the instructions for connecting the power switch and LED pins to the Raspberry Pi:

### Pin Diagram

Refer to the following pin diagram for Raspberry Pi Zero 2W to identify the GPIO pins:

![Raspberry Pi Zero 2W Pinout](./images/raspi-zero2w-pin.jpg)

### Power Switch Pin Installation

- Connect one pin of the power switch to any 3.3V or 5V pin on the Raspberry Pi.
- Connect the other pin of the power switch to a GPIO pin (e.g., GPIO24).

### LED Pin Installation

- Connect the positive leg (longer leg) of the LED to a GPIO pin (e.g., GPIO23).
- Connect the negative leg (shorter leg) of the LED to a Ground (GND) pin on the Raspberry Pi.

Ensure the connections are secure and double-check the GPIO pin numbers used in your script.

### Update the Script for Pin Configuration

After installing the power switch and LED pins, update the `raspi-wol.py` script to match the GPIO pins you used. Open the script and modify the following lines:

- Update the `RELAY_PIN` variable to the GPIO pin connected to the power switch:
  ```python
  RELAY_PIN = <your_relay_gpio_pin>
  ```

- Update the `LED_PIN` variable to the GPIO pin connected to the LED:
  ```python
  LED_PIN = <your_led_gpio_pin>
  ```

Replace `<your_relay_gpio_pin>` and `<your_led_gpio_pin>` with the actual GPIO pin numbers you used during installation.

### Update the Systemd Service File

Before proceeding, ensure the `raspi-wol@.service` file is updated with the correct working directory and script path. Open the file and modify the following lines:

- Update the `ExecStart` line to point to the correct path of the `raspi-wol.py` script:
  ```
  ExecStart=/usr/bin/python3 /path/to/raspi-wol/raspi-wol.py %I
  ```

- Update the `WorkingDirectory` line to the directory where the project is located:
  ```
  WorkingDirectory=/path/to/raspi-wol/
  ```

Replace `/path/to/raspi-wol/` with the actual path where the project is cloned.

## Installation

1. Clone this repository to your Raspberry Pi:
   ```bash
   git clone <repository-url>
   cd raspi-wol
   ```

2. Install required Python libraries:
   ```bash
   pip install RPi.GPIO
   ```

3. Set up the systemd service:
   - Copy the `raspi-wol@.service` file to the systemd directory:
     ```bash
     sudo cp raspi-wol@.service /etc/systemd/system/
     ```

   - Reload systemd to recognize the new service:
     ```bash
     sudo systemctl daemon-reload
     ```

## Usage

### Starting the Service

The service is instantiated using the `@` symbol followed by the MAC address and IP address of the target device, separated by an underscore (`_`). For example:

```bash
sudo systemctl start raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
```

### Enabling the Service at Boot

To enable the service to start automatically on boot, use the following command:

```bash
sudo systemctl enable raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
```

### Stopping the Service

To stop the service, use:

```bash
sudo systemctl stop raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
```

### Disabling the Service

To disable the service from starting at boot, use:

```bash
sudo systemctl disable raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
```

## Example

Here are some example MAC addresses and IPs you can use:

- MAC Address: `AA:BB:CC:DD:EE:FF`, IP: `192.168.1.100`
- MAC Address: `11:22:33:44:55:66`, IP: `192.168.1.101`

To start the service for the first example:

```bash
sudo systemctl start raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
```

## Updating the Service

If you make changes to the `raspi-wol@.service` file or other project files, you can use the `update-service.sh` script to update and restart the service. Follow these steps:

1. Ensure you are in the project directory:
   ```bash
   cd /path/to/raspi-wol
   ```

2. Run the `update-service.sh` script:
   ```bash
   ./update-service.sh
   ```

   This script will:
   - Pull the latest changes from the repository.
   - Stop the currently running service.
   - Copy the updated `raspi-wol@.service` file to `/etc/systemd/system/`.
   - Reload the systemd daemon.
   - Restart the service.

3. Verify the service is running:
   ```bash
   sudo systemctl status raspi-wol@<MAC_ADDRESS>_<IP_ADDRESS>.service
   ```

Replace `<MAC_ADDRESS>` and `<IP_ADDRESS>` with the appropriate values for your setup.

## Troubleshooting

- Check the service logs for debugging:
  ```bash
  sudo journalctl -u raspi-wol@AA:BB:CC:DD:EE:FF_192.168.1.100.service
  ```

- Ensure the MAC address and IP address are correctly formatted as `<MAC_ADDRESS>_<PING_IP>`.

- Verify the GPIO pins are correctly connected and configured.

