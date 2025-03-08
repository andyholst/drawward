#!/usr/bin/env python3
import os
from pathlib import Path
import xmltodict
import yaml

INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

def parse_xml_to_dict(xml_file):
    """Parse an XML file into a Python dictionary."""
    try:
        with open(xml_file, 'r') as f:
            return xmltodict.parse(f.read())
    except Exception as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return None

def generate_catalog_entries():
    """Generate Backstage catalog YAML files from C4 model XML files."""
    xml_files = list(Path(INPUT_DIR).glob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {INPUT_DIR}")
        exit(0)

    # Data structures to collect elements
    systems = {}
    containers = {}
    components = {}
    resources = {}

    # Step 1: Collect data from all XML files
    for xml_file in xml_files:
        print(f"Processing {xml_file}...")
        data = parse_xml_to_dict(xml_file)
        if not data:
            continue
        try:
            objects = data['mxfile']['diagram']['mxGraphModel']['root'].get('object', [])
            if not isinstance(objects, list):
                objects = [objects] if objects else []
        except KeyError as e:
            print(f"Error: Missing expected key {e} in {xml_file}")
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            c4_type = obj.get('@c4Type')
            c4_name = obj.get('@c4Name', '')

            if c4_type == 'Software System':
                if c4_name not in systems:
                    systems[c4_name] = {
                        'description': obj.get('@c4Description', '')
                    }
            elif c4_type == 'Container':
                if c4_name not in containers:
                    containers[c4_name] = {
                        'description': obj.get('@c4Description', ''),
                        'technology': obj.get('@c4Technology', '')
                    }
            elif c4_type == 'Component':
                if c4_name not in components:
                    components[c4_name] = {
                        'description': obj.get('@c4Description', ''),
                        'technology': obj.get('@c4Technology', '')
                    }
            elif c4_type == 'Database':
                c4_container = obj.get('@c4Container', '')
                if c4_container and c4_container not in resources:
                    resources[c4_container] = {
                        'name': 'database-' + c4_container.lower().replace('/', '-').replace(' ', '-'),
                        'description': obj.get('@c4Description', ''),
                        'technology': obj.get('@c4Technology', '')
                    }

    # Step 2: Generate catalog entries
    catalog_entries = {}

    # Initialize catalog files
    output_file_system = Path(OUTPUT_DIR) / 'system' / 'catalog-info.yaml'
    output_file_container = Path(OUTPUT_DIR) / 'container' / 'catalog-info.yaml'
    output_file_component = Path(OUTPUT_DIR) / 'component' / 'catalog-info.yaml'
    catalog_entries[output_file_system] = []
    catalog_entries[output_file_container] = []
    catalog_entries[output_file_component] = []

    # Generate System entries
    for c4_name, details in systems.items():
        unique_name = c4_name.lower().replace(' ', '-')
        entry = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': 'System',
            'metadata': {
                'name': unique_name,
                'namespace': 'default',
                'description': details['description']
            },
            'spec': {
                'owner': 'team-a'
            }
        }
        catalog_entries[output_file_system].append(entry)

    # Generate Component entries for Containers (type: service) in container level
    for c4_name, details in containers.items():
        unique_name = c4_name.lower().replace(' ', '-')
        entry = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': 'Component',
            'metadata': {
                'name': unique_name,
                'namespace': 'default',
                'description': details['description']
            },
            'spec': {
                'type': 'service',
                'lifecycle': 'production',
                'owner': 'team-a'
            }
        }
        if details['technology']:
            entry['spec']['technology'] = details['technology']
        catalog_entries[output_file_container].append(entry)

    # Generate Resource entries for Databases (type: database) in both levels
    for resource in resources.values():
        entry = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': 'Resource',
            'metadata': {
                'name': resource['name'],
                'namespace': 'default',
                'description': resource['description']
            },
            'spec': {
                'type': 'database',
                'owner': 'team-a',
                'technology': resource['technology']
            }
        }
        catalog_entries[output_file_container].append(entry)
        catalog_entries[output_file_component].append(entry)

    # Generate Component entries for Components (type: library) in component level
    for c4_name, details in components.items():
        unique_name = c4_name.lower().replace(' ', '-')
        entry = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': 'Component',
            'metadata': {
                'name': unique_name,
                'namespace': 'default',
                'description': details['description']
            },
            'spec': {
                'type': 'library',
                'lifecycle': 'production',
                'owner': 'team-a',
                'technology': details['technology']
            }
        }
        catalog_entries[output_file_component].append(entry)

    # Step 3: Write catalog entries to YAML files
    for output_file, entries in catalog_entries.items():
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            yaml.dump_all(entries, f, explicit_start=True, default_flow_style=False, Dumper=yaml.SafeDumper)

    # Step 4: Validate output files
    missing_or_empty = [
        f"{file} is {'missing' if not file.exists() else 'empty'}"
        for file in catalog_entries
        if not file.exists() or file.stat().st_size == 0
    ]
    if missing_or_empty:
        print("Validation failed:")
        print("\n".join(f" - {error}" for error in missing_or_empty))
        exit(1)
    else:
        print("Validation succeeded:")
        print("\n".join(f" - {file}" for file in catalog_entries))

if __name__ == "__main__":
    generate_catalog_entries()
