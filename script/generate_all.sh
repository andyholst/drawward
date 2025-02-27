#!/bin/bash

SVG_DIR="docs/design/drawio"
XML_DIR="docs/design/xml"
DRAWIO_PATH="/Applications/draw.io.app/Contents/MacOS/draw.io"

# Step 1: Export SVGs to XML
for SVG_FILE in "$SVG_DIR"/*.svg; do
    XML_FILE="$XML_DIR/$(basename "$SVG_FILE" .svg).xml"
    "$DRAWIO_PATH" --export --format xml --output "$XML_FILE" "$SVG_FILE" || { echo "Export failed for $SVG_FILE"; exit 1; }
done

# Step 2: Generate Backstage files
python script/generate_backstage_from_xml.py || { echo "Generation failed"; exit 1; }

echo "Backstage files generated in docs/design/backstage"