#!/usr/bin/env python3
import os
from pathlib import Path
import xmltodict
import yaml

# Define input and output directories
INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

# Read environment variables with defaults
REPO_SLUG = os.getenv('REPO_SLUG', 'org/repo')      # GitHub repository slug
TEAM_NAME = os.getenv('TEAM_NAME', 'team-a')        # Team name
OWNER = os.getenv('OWNER', TEAM_NAME)               # Owner (defaults to TEAM_NAME)
LIFECYCLE = os.getenv('LIFECYCLE', 'production')    # Lifecycle stage

def parse_xml_to_dict(xml_file):
    """Parse an XML file into a Python dictionary."""
    with open(xml_file, 'r') as f:
        return xmltodict.parse(f.read())

def sanitize_name(name):
    """Convert a name to a lowercase, hyphen-separated string."""
    return name.lower().replace(' ', '-').replace('/', '-')

def generate_entity_ref(kind, name):
    """Generate a Backstage entity reference (e.g., 'component:postgres-repository')."""
    return f"{kind}:{name}"

def process_xml_file(xml_file):
    """Process an XML file and return entities and relationships."""
    data = parse_xml_to_dict(xml_file)
    root = data['mxfile']['diagram']['mxGraphModel']['root']

    # Extract parent system from boundary
    boundary = next((obj for obj in root.get('object', []) if obj.get('@c4Type') in ['SystemScopeBoundary', 'ContainerScopeBoundary']), None)
    parent_system = sanitize_name(boundary['@c4Name']) if boundary else None
    print(f"Processing {xml_file}: Boundary = {parent_system or 'None'}")

    # Collect entities, including 'Person'
    entities = {}
    for obj in root.get('object', []):
        if '@c4Type' not in obj:
            continue
        c4_type = obj['@c4Type']
        if c4_type in ['Software System', 'Container', 'Component', 'Database', 'Person']:
            name = sanitize_name(obj.get('@c4Name', obj.get('@c4Container', '')))
            kind = {
                'Software System': 'system',
                'Container': 'component',
                'Component': 'component',
                'Database': 'resource',
                'Person': 'user'
            }[c4_type]
            entities[obj['@id']] = {
                'kind': kind,
                'name': name,
                'description': obj.get('@c4Description', ''),
                'technology': obj.get('@c4Technology', ''),
                'type': (
                    'service' if c4_type == 'Container' else
                    'library' if c4_type == 'Component' else
                    'database' if c4_type == 'Database' else
                    'user' if c4_type == 'Person' else
                    'system'
                ),
                'system': parent_system if kind not in ['system', 'user'] and parent_system else None,
                'dependsOn': [],
                'providesApis': [],
                'consumesApis': []
            }
            print(f"Entity: {name} ({kind}, ID={obj['@id']})")

    # Collect relationships and identify API interactions
    api_counter = 0
    for obj in root.get('object', []):
        if obj.get('@c4Type') == 'Relationship':
            mxcell = obj.get('mxCell')
            if isinstance(mxcell, dict) and mxcell.get('@edge') == '1':
                source_id = mxcell.get('@source')
                target_id = mxcell.get('@target')
                technology = obj.get('@c4Technology', '').lower()
                description = obj.get('@c4Description', '')
                if source_id in entities and target_id in entities:
                    source = entities[source_id]
                    target = entities[target_id]
                    if 'json/http' in technology or 'api' in description.lower():
                        # This is an API relationship
                        api_name = sanitize_name(f"api-{description}")
                        api_ref = generate_entity_ref('api', api_name)
                        # Link provider (target) to the API
                        target['providesApis'].append(api_ref)
                        # Link consumer (source) to the API
                        source['consumesApis'].append(api_ref)
                        # Create API entity with all required keys
                        api_entity = {
                            'kind': 'api',
                            'name': api_name,
                            'description': description,
                            'technology': technology,
                            'type': 'openapi',  # Default type, adjustable
                            'lifecycle': LIFECYCLE,
                            'owner': OWNER,
                            'system': parent_system,
                            'dependsOn': [],       # Added
                            'providesApis': [],    # Added
                            'consumesApis': []     # Added
                        }
                        entities[f"api_{api_counter}"] = api_entity
                        api_counter += 1
                        print(f"API Relationship: {source['name']} consumes {api_ref}, {target['name']} provides {api_ref}")
                    else:
                        # Regular dependency
                        source['dependsOn'].append(generate_entity_ref(target['kind'], target['name']))
                        print(f"Added: {source['name']} dependsOn {target['name']}")
                else:
                    print(f"Error: Source {source_id} or Target {target_id} not found in entities")

    return entities

def generate_catalog_files():
    """Generate Backstage catalog YAML files from all XML files."""
    xml_files = list(Path(INPUT_DIR).glob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {INPUT_DIR}")
        exit(0)

    all_entities = {}
    for xml_file in xml_files:
        entities = process_xml_file(xml_file)
        for entity_id, entity in entities.items():
            key = (entity['kind'], entity['name'])
            if key not in all_entities:
                all_entities[key] = entity
            else:
                # Merge relationships, avoiding duplicates
                all_entities[key]['dependsOn'].extend(
                    [dep for dep in entity['dependsOn'] if dep not in all_entities[key]['dependsOn']]
                )
                all_entities[key]['providesApis'].extend(
                    [api for api in entity['providesApis'] if api not in all_entities[key]['providesApis']]
                )
                all_entities[key]['consumesApis'].extend(
                    [api for api in entity['consumesApis'] if api not in all_entities[key]['consumesApis']]
                )

    # Generate YAML files for entities
    for (kind, name), entity in all_entities.items():
        output_dir = Path(OUTPUT_DIR) / f"{kind}s"
        output_file = output_dir / f"{name}.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        yaml_data = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': entity['kind'].capitalize(),
            'metadata': {
                'name': entity['name'],
                'description': entity['description'],
                'annotations': {
                    'github.com/project-slug': REPO_SLUG
                },
                'tags': [entity['technology'].lower()] if entity['technology'] else []
            },
            'spec': {
                'type': entity['type'],
                'lifecycle': LIFECYCLE,
                'owner': OWNER
            }
        }
        if entity['system']:
            yaml_data['spec']['system'] = entity['system']
        if entity['dependsOn']:
            yaml_data['spec']['dependsOn'] = entity['dependsOn']
        if entity['providesApis']:
            yaml_data['spec']['providesApis'] = entity['providesApis']
        if entity['consumesApis']:
            yaml_data['spec']['consumesApis'] = entity['consumesApis']
        if entity['technology'] and entity['kind'] != 'api':
            yaml_data['spec']['technology'] = entity['technology']

        with open(output_file, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False)
        print(f"Generated: {output_file}")

if __name__ == "__main__":
    generate_catalog_files()
