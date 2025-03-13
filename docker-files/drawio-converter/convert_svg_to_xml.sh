#!/bin/bash

# Use the XML_DIR set by entrypoint.sh
if [ -z "$XML_DIR" ]; then
    echo "Error: XML_DIR is not set."
    exit 1
fi

# Check if input directory is mounted
if [ ! -d "$SVG_DIR" ]; then
    echo "Error: Input directory $SVG_DIR is not mounted."
    exit 1
fi

# Find all SVG files recursively in /input
SVG_FILES=$(find "$SVG_DIR" -type f -name "*.svg")

# Handle cases with no SVG files
if [ -z "$SVG_FILES" ]; then
    echo "Error: No SVG files found in $SVG_DIR or its subdirectories"
    exit 1
fi

# Bypass DBus to avoid connection issues
export DBUS_SESSION_BUS_ADDRESS=/dev/null

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1024x768x16 &
export DISPLAY=:99

# Process each SVG file
for SVG_FILE in $SVG_FILES; do
    XML_FILE="$XML_DIR/$(basename "$SVG_FILE" .svg).xml"
    
    # Verify input file exists
    if [ ! -f "$SVG_FILE" ]; then
        echo "Error: Input file $SVG_FILE does not exist"
        exit 1
    fi
    
    echo "Converting $SVG_FILE to $XML_FILE..."
    
    drawio --no-sandbox --export --format xml --output "$XML_FILE" "$SVG_FILE" > /tmp/drawio.log 2>&1
    EXIT_STATUS=$?
    
    # Check if drawio command was successful
    if [ $EXIT_STATUS -ne 0 ]; then
        echo "Error: drawio failed with exit status $EXIT_STATUS"
        echo "drawio output:"
        cat /tmp/drawio.log
        exit 1
    fi
    
    # Check if XML file was created
    if [ ! -f "$XML_FILE" ]; then
        echo "Error: XML file $XML_FILE was not created"
        exit 1
    fi
    
    # Check if XML file is not empty
    if [ ! -s "$XML_FILE" ]; then
        echo "Error: XML file $XML_FILE is empty"
        exit 1
    fi
    
    echo "Successfully converted $SVG_FILE to $XML_FILE"
done

exit 0
