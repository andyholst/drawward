#!/usr/bin/env python3

import os
from pathlib import Path
import xmltodict
import yaml

# Define input and output directories
INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

existing_names = {
    'System': set(),
    'Component': set(),
    'Resource': set()
}

def parse_xml_to_dict(xml_file):
    """Parse an XML file into a Python dictionary."""
    try:
        with open(xml_file, 'r') as f:
            return xmltodict.parse(f.read())
    except Exception as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return None

def make_unique_name(base_name, kind):
    """Generate a unique name by appending a suffix if necessary."""
    name = base_name.lower().replace(' ', '-')
    counter = 1
    unique_name = name
    while unique_name in existing_names[kind]:
        unique_name = f"{name}-{counter}"
        counter += 1
    existing_names[kind].add(unique_name)
    return unique_name

def generate_catalog_entry(c4_element, expected_files):
    """Generate a catalog entry from a C4 element and track the expected file."""
    # Extract attributes from the XML element
    c4_type = c4_element.get('@c4Type', '')
    c4_name = c4_element.get('@c4Name', '')
    c4_description = c4_element.get('@c4Description', '')
    c4_technology = c4_element.get('@c4Technology', '')

    # Skip if required fields are missing
    if not c4_type or not c4_name:
        print(f"Skipping element: Missing c4Type or c4Name in {c4_element}")
        return None

    # Determine the Backstage kind and output directory
    if c4_type == 'SystemScopeBoundary':
        kind = 'System'
        output_dir = Path(OUTPUT_DIR) / 'system'
    elif c4_type == 'ContainerScopeBoundary':
        kind = 'Component'
        output_dir = Path(OUTPUT_DIR) / 'container'
    elif c4_type == 'Component':
        kind = 'Component'
        output_dir = Path(OUTPUT_DIR) / 'component'
    elif c4_type == 'Database':
        kind = 'Resource'
        output_dir = Path(OUTPUT_DIR) / 'component'
    else:
        print(f"Skipping unsupported c4Type: {c4_type}")
        return None

    # Generate a unique name
    base_name = c4_name
    unique_name = make_unique_name(base_name, kind)

    # Define the catalog entry structure with namespace
    catalog_entry = {
        'apiVersion': 'backstage.io/v1alpha1',
        'kind': kind,
        'metadata': {
            'name': unique_name,
            'namespace': 'default',  # Ensures compliance with Backstage schema
            'description': c4_description
        },
        'spec': {}
    }

    # Add spec details based on kind
    if kind == 'System':
        catalog_entry['spec']['owner'] = 'team-a'
    elif kind == 'Component':
        catalog_entry['spec'] = {
            'type': 'service' if c4_type == 'ContainerScopeBoundary' else 'library',
            'lifecycle': 'production',
            'owner': 'team-a'
        }
        if c4_technology:
            catalog_entry['spec']['technology'] = c4_technology
    elif kind == 'Resource':
        catalog_entry['spec'] = {
            'type': 'database',
            'owner': 'team-a'
        }
        if c4_technology:
            catalog_entry['spec']['technology'] = c4_technology

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'catalog-info.yaml'
    expected_files.add(output_file)

    # Append to or create the catalog file
    if output_file.exists():
        with open(output_file, 'r') as f:
            existing_data = yaml.safe_load(f) or []
        if not isinstance(existing_data, list):
            existing_data = [existing_data]
        existing_data.append(catalog_entry)
    else:
        existing_data = [catalog_entry]

    with open(output_file, 'w') as f:
        yaml.safe_dump(existing_data, f, default_flow_style=False)

    return output_file

def main():
    """Process XML files, generate YAML files, and validate their existence."""
    # Find all XML files in the input directory
    xml_files = list(Path(INPUT_DIR).glob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {INPUT_DIR}")
        exit(0)

    # Set to track expected YAML files
    expected_files = set()

    # Process each XML file
    for xml_file in xml_files:
        print(f"Processing {xml_file}...")
        data = parse_xml_to_dict(xml_file)
        if not data:
            continue

        # Extract mxGraphModel root objects
        try:
            diagram = data['mxfile']['diagram']
            root = diagram['mxGraphModel']['root']
            objects = root.get('object', [])
            if not isinstance(objects, list):
                objects = [objects] if objects else []
        except KeyError as e:
            print(f"Error: Missing expected key {e} in {xml_file}")
            continue

        # Generate catalog entries for each object
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            catalog_file = generate_catalog_entry(obj, expected_files)
            if catalog_file:
                print(f"Generated catalog entry in {catalog_file}")

    # Check if any YAML files were expected
    if not expected_files:
        print("Warning: No YAML files were generated from the XML files.")
        exit(0)

    # Validate that all expected files exist and are non-empty
    missing_or_empty = []
    for file in expected_files:
        if not file.exists():
            missing_or_empty.append(f"{file} is missing")
        elif file.stat().st_size == 0:
            missing_or_empty.append(f"{file} is empty")

    # Report results
    if missing_or_empty:
        print("Validation failed:")
        for error in missing_or_empty:
            print(f" - {error}")
        exit(1)
    else:
        print("Validation succeeded: All expected YAML files exist and are non-empty.")
        print("Generated YAML files:")
        for file in expected_files:
            print(f" - {file}")

if __name__ == "__main__":
    main()
