#!/bin/bash

SERVICE_NAME="raspi-wol@10:FF:E0:B1:6E:F1_10.11.12.240.service"
SERVICE_FILE="raspi-wol@.service"

# Pull the latest changes from the repository
echo "Pulling the latest changes from the repository..."
git pull

# Stop the service
echo "Stopping $SERVICE_NAME..."
sudo systemctl stop "$SERVICE_NAME"

# Copy the new service file
echo "Copying $SERVICE_FILE to /etc/systemd/system/..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Start the service
echo "Starting $SERVICE_NAME..."
sudo systemctl start "$SERVICE_NAME"

echo "$SERVICE_NAME updated and restarted successfully."
