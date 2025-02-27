import os
import xml.etree.ElementTree as ET

svg_dir = "docs/design/drawio"
xml_dir = "docs/design/xml"
os.makedirs(xml_dir, exist_ok=True)

for svg_file in ["System.svg", "Container.svg", "Component.svg"]:
    svg_path = os.path.join(svg_dir, svg_file)
    xml_path = os.path.join(xml_dir, svg_file.replace(".svg", ".xml"))

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Extract XML from SVG (draw.io embeds it in a data URI or <mxfile>)
    start_marker = "<mxfile"
    end_marker = "</mxfile>"
    if start_marker in svg_content:
        start_idx = svg_content.index(start_marker)
        end_idx = svg_content.index(end_marker) + len(end_marker)
        xml_content = svg_content[start_idx:end_idx]
        
        # Write extracted XML
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        # Validate XML
        ET.parse(xml_path)
        print(f"Extracted {svg_file} to {xml_path}")
    else:
        raise ValueError(f"No XML found in {svg_file}")