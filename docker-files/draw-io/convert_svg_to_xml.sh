#!/bin/bash

# Ensure /var/run/dbus/ exists at runtime
echo "Setting up DBus directory..."
mkdir -p /var/run/dbus
chmod 755 /var/run/dbus

# Start DBus daemon in the background
echo "Starting DBus daemon..."
dbus-daemon --system --fork 2>/tmp/dbus_error.log
sleep 1  # Give it a moment to start

SVG_DIR="/input"
XML_DIR="/output"

if [ ! -d "$SVG_DIR" ] || [ ! -d "$XML_DIR" ]; then
    echo "Error: Please mount input and output directories."
    exit 1
fi

shopt -s nullglob
SVG_FILES=("$SVG_DIR"/*.svg)
if [ ${#SVG_FILES[@]} -eq 0 ]; then
    echo "No SVG files found in $SVG_DIR"
    exit 0
fi

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1024x768x16 &
XVFB_PID=$!
sleep 1
export DISPLAY=:99

for SVG_FILE in "${SVG_FILES[@]}"; do
    XML_FILE="$XML_DIR/$(basename "$SVG_FILE" .svg).xml"
    
    if [ ! -f "$SVG_FILE" ]; then
        echo "Error: Input file $SVG_FILE does not exist"
        kill $XVFB_PID
        exit 1
    fi
    
    echo "Converting $SVG_FILE to $XML_FILE..."
    /usr/bin/drawio --no-sandbox --disable-gpu --export --format xml --output "$XML_FILE" "$SVG_FILE" 2>/tmp/drawio_error.log
    if [ $? -ne 0 ]; then
        echo "Failed to convert $SVG_FILE"
        cat /tmp/drawio_error.log
        kill $XVFB_PID
        exit 1
    else
        echo "Successfully converted $SVG_FILE to $XML_FILE"
    fi
done

echo "Stopping Xvfb..."
kill $XVFB_PID
rm -f /tmp/drawio_error.log /tmp/dbus_error.log

exit 0
