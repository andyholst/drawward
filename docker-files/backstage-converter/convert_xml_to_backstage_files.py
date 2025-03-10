#!/usr/bin/env python3
import os
from pathlib import Path
import xmltodict
import yaml
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory and environment variables
INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

REPO_SLUG = os.getenv('REPO_SLUG', 'org/repo')
TEAM_NAME = os.getenv('TEAM_NAME', 'team-a')
OWNER = os.getenv('OWNER', TEAM_NAME)
LIFECYCLE = os.getenv('LIFECYCLE', 'production')

# API technology mappings
API_TECHNOLOGIES = ['json/http', 'grpc', 'graphql', 'soap', 'wsdl', 'odata', 'raml', 'websocket']
API_TYPE_MAPPING = {
    'json/http': 'openapi',
    'grpc': 'grpc',
    'graphql': 'graphql',
    'soap': 'soap',
    'wsdl': 'soap',
    'websocket': 'websocket',
    'odata': 'odata',
    'raml': 'openapi',
}

# Infrastructure technologies
INFRA_TECHNOLOGIES = [
    'postgresql', 'redis', 'apache kafka', 'hashcorp vault', 'mysql', 'mongodb',
    's3', 'sns', 'sqs', 'dynamodb', 'elasticsearch', 'rabbitmq', 'activemq',
    'zeromq', 'nats', 'pubsub', 'servicebus'
]

def parse_xml_to_dict(xml_file):
    """Parse an XML file into a Python dictionary."""
    with open(xml_file, 'r') as f:
        return xmltodict.parse(f.read())

def sanitize_name(name):
    """Convert a name to a lowercase, hyphen-separated string."""
    name = name.lower().replace(' ', '-').replace('/', '-')
    return re.sub(r'-+', '-', name)

def generate_entity_ref(kind, name):
    """Generate a Backstage entity reference (e.g., 'component:authorization-service')."""
    return f"{kind}:{name}"

def refine_tags_and_technology(entity, container_name=None):
    """Refine tags and technology based on entity type and description."""
    if 'type' not in entity:
        entity['tags'] = []
        return entity

    tech = entity.get('technology', '').lower()
    description = entity.get('description', '').lower()
    tags = [tech] if tech else []
    refined_tech = tech

    if entity['type'] == 'library':
        if any(t in tech for t in ['spring', 'spring boot', 'spring-boot']):
            if 'database' in description or 'postgres' in description:
                tags = ['spring-data', 'database-library']
                refined_tech = 'Spring Data JPA'
            else:
                tags = ['spring-library']
                refined_tech = 'Spring Framework'
        if container_name:
            tags.append(f"{container_name}-library")
    elif entity['type'] == 'service':
        if any(t in tech for t in ['spring', 'spring boot', 'spring-boot']):
            tags = ['spring-service']
            refined_tech = 'Spring Boot Service'

    entity['tags'] = tags
    if refined_tech:
        entity['technology'] = refined_tech
    logger.info(f"Refined {entity['name']}: tags={tags}, technology={refined_tech}")
    return entity

def process_xml_file(xml_file):
    """Process an XML file and return entities and relationships."""
    data = parse_xml_to_dict(xml_file)
    root = data['mxfile']['diagram']['mxGraphModel']['root']

    system_boundary = next(
        (obj for obj in root.get('object', []) if obj.get('@c4Type') == 'SystemScopeBoundary'), None
    )
    container_boundary = next(
        (obj for obj in root.get('object', []) if obj.get('@c4Type') == 'ContainerScopeBoundary'), None
    )
    parent_system = sanitize_name(system_boundary['@c4Name']) if system_boundary else None
    parent_container = sanitize_name(container_boundary['@c4Name']) if container_boundary else None
    logger.info(f"Processing {xml_file}: System = {parent_system or 'None'}, Container = {parent_container or 'None'}")

    entities = {}

    if system_boundary:
        system_name = sanitize_name(system_boundary['@c4Name'])
        system_entity = {
            'kind': 'system',
            'name': system_name,
            'description': system_boundary.get('@c4Description', ''),
            'system': None,
            'dependsOn': [],
            'providesApis': [],
            'consumesApis': []
        }
        entities['system_boundary'] = system_entity
        logger.info(f"System Entity: {system_name} (system)")

    for obj in root.get('object', []):
        if '@c4Type' not in obj:
            continue
        c4_type = obj.get('@c4Type')
        technology = obj.get('@c4Technology', '').lower()

        if c4_type in ['SystemScopeBoundary', 'ContainerScopeBoundary']:
            continue

        name = obj.get('@c4Name')
        if not name:
            c4_type_lower = c4_type.lower()
            if 'database' in c4_type_lower:
                db_type = c4_type_lower.split()[0] if len(c4_type_lower.split()) > 1 else technology
                name = f"{db_type}-database"
            else:
                name = technology or obj.get('@c4Container', 'unknown')
            if name in ['container', 'unknown', '']:
                name = f"{name}-{obj['@id']}"
        name = sanitize_name(name)

        if c4_type == 'Software System':
            kind = 'component'
            entity_type = 'service'
        elif c4_type == 'Container':
            if technology in INFRA_TECHNOLOGIES:
                kind = 'resource'
                entity_type = (
                    'database' if 'sql' in technology or 'mongo' in technology or 'redis' in technology else
                    'message-queue' if 'kafka' in technology or 'mq' in technology or 'pubsub' in technology else
                    'key-vault' if 'vault' in technology else 'infrastructure'
                )
            else:
                kind = 'component'
                entity_type = 'service'
        elif c4_type == 'Component':
            kind = 'component'
            entity_type = 'library'
        elif c4_type == 'Person':
            kind = 'user'
            entity_type = 'user'
        elif c4_type.lower().endswith('database'):
            kind = 'resource'
            entity_type = 'database'
        elif technology in INFRA_TECHNOLOGIES:
            kind = 'resource'
            entity_type = (
                'database' if 'sql' in technology or 'mongo' in technology or 'redis' in technology else
                'message-queue' if 'kafka' in technology or 'mq' in technology or 'pubsub' in technology else
                'key-vault' if 'vault' in technology else 'infrastructure'
            )
        else:
            if c4_type != 'Relationship':
                logger.warning(f"Unknown c4Type: {c4_type}")
            continue

        system = parent_system if kind in ['component', 'resource'] and parent_system else None
        container = parent_container if kind == 'component' and entity_type == 'library' and parent_container else None

        entity = {
            'kind': kind,
            'name': name,
            'description': obj.get('@c4Description', ''),
            'technology': obj.get('@c4Technology', ''),
            'type': entity_type,
            'system': system,
            'container': container,
            'dependsOn': [],
            'providesApis': [],
            'consumesApis': []
        }
        entities[obj['@id']] = entity
        logger.info(f"Entity: {name} ({kind}), System = {entity['system']}, Container = {entity.get('container', 'None')}, ID = {obj['@id']}")

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
                    if technology in API_TECHNOLOGIES:
                        api_name = sanitize_name(f"api-{description}")
                        api_ref = generate_entity_ref('api', api_name)
                        api_type = API_TYPE_MAPPING.get(technology, 'openapi')
                        if api_ref not in target['providesApis']:
                            target['providesApis'].append(api_ref)
                        if api_ref not in source['consumesApis']:
                            source['consumesApis'].append(api_ref)
                        api_system = target['system']
                        api_entity = {
                            'kind': 'api',
                            'name': api_name,
                            'description': description,
                            'technology': technology,
                            'type': api_type,
                            'lifecycle': LIFECYCLE,
                            'owner': OWNER,
                            'system': api_system,
                            'dependsOn': [],
                            'providesApis': [],
                            'consumesApis': []
                        }
                        entities[f"api_{api_counter}"] = api_entity
                        api_counter += 1
                        logger.info(f"API: {api_name}, System = {api_system}, Source = {source['name']}, Target = {target['name']}")
                    else:
                        dep = generate_entity_ref(target['kind'], target['name'])
                        if dep not in source['dependsOn']:
                            source['dependsOn'].append(dep)
                        logger.info(f"Dependency: {source['name']} dependsOn {dep}")

    return entities

def generate_catalog_files():
    """Generate Backstage catalog YAML files from all XML files."""
    xml_files = list(Path(INPUT_DIR).glob('*.xml'))
    if not xml_files:
        logger.error(f"No XML files found in {INPUT_DIR}")
        exit(0)

    all_entities = {}
    for xml_file in xml_files:
        entities = process_xml_file(xml_file)
        for entity_id, entity in entities.items():
            key = (entity['kind'], entity['name'])
            if key not in all_entities:
                all_entities[key] = entity
            else:
                # Merge attributes if more detailed
                existing = all_entities[key]
                if len(entity.get('description', '')) > len(existing.get('description', '')):
                    existing['description'] = entity['description']
                if entity.get('technology') and not existing.get('technology'):
                    existing['technology'] = entity['technology']
                existing['dependsOn'].extend(
                    [dep for dep in entity['dependsOn'] if dep not in existing['dependsOn']]
                )
                existing['providesApis'].extend(
                    [api for api in entity['providesApis'] if api not in existing['providesApis']]
                )
                existing['consumesApis'].extend(
                    [api for api in entity['consumesApis'] if api not in existing['consumesApis']]
                )

    for (kind, name), entity in all_entities.items():
        container_name = entity.get('container')
        entity = refine_tags_and_technology(entity, container_name)

        output_dir = Path(OUTPUT_DIR) / f"{kind}s"
        output_file = output_dir / f"{name}.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        yaml_data = {
            'apiVersion': 'backstage.io/v1alpha1',
            'kind': entity['kind'].capitalize(),
            'metadata': {
                'name': entity['name'],
                'description': entity.get('description', ''),
                'annotations': {'github.com/project-slug': REPO_SLUG},
                'tags': entity.get('tags', [])
            },
            'spec': {
                'lifecycle': LIFECYCLE,
                'owner': OWNER
            }
        }
        if 'type' in entity:
            yaml_data['spec']['type'] = entity['type']
        if entity['system'] and entity['kind'] in ['component', 'resource', 'api']:
            yaml_data['spec']['system'] = entity['system']
        if entity['dependsOn']:
            yaml_data['spec']['dependsOn'] = entity['dependsOn']
        if entity['providesApis']:
            yaml_data['spec']['providesApis'] = entity['providesApis']
        if entity['consumesApis']:
            yaml_data['spec']['consumesApis'] = entity['consumesApis']
        if entity.get('technology') and entity['kind'] != 'api':
            yaml_data['spec']['technology'] = entity['technology']

        with open(output_file, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False)
        logger.info(f"Generated: {output_file} with system = {entity.get('system', 'None')}")

if __name__ == "__main__":
    generate_catalog_files()
