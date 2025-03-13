#!/bin/bash
COMMAND=$1

case $COMMAND in
  convert-svg-to-yaml)
    # Create a temporary directory for XML files
    mkdir -p /tmp/xml || {
      echo "Error: Failed to create temporary XML directory"
      exit 1
    }

    # Step 1: Convert SVG to XML into /tmp/xml
    export SVG_DIR="/input"
    export XML_DIR="/tmp/xml"
    /usr/local/bin/convert_svg_to_xml.sh || {
      echo "Error: SVG to XML conversion failed"
      exit 1
    }

    # Step 2: Convert XML to YAML, outputting to /output
    export INPUT_DIR="/tmp/xml"
    export OUTPUT_DIR="/output"
    /usr/local/bin/convert_xml_to_backstage_files.py || {
      echo "Error: XML to YAML conversion failed"
      exit 1
    }

    # Clean up temporary XML files
    rm -rf /tmp/xml || {
      echo "Warning: Failed to clean up temporary XML files"
    }

    echo "Conversion complete: SVG files from /input converted to YAML in /output"
    ;;
  *)
    echo "Error: Invalid command '$COMMAND'"
    echo "Usage: docker run <image> convert-svg-to-yaml"
    echo "Description: Converts SVG files to Backstage YAML files in one step"
    echo "  Mount /input with SVG files (e.g., *.svg)"
    echo "  Mount /output for YAML results (e.g., catalog files)"
    echo "  Optional environment variables:"
    echo "    REPO_SLUG (default: org/repo)"
    echo "    TEAM_NAME (default: team-a)"
    echo "    OWNER (default: TEAM_NAME)"
    echo "    LIFECYCLE (default: production)"
    exit 1
    ;;
esac
