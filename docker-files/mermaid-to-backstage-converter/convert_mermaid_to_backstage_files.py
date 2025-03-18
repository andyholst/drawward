#!/usr/bin/env python3
import os
from pathlib import Path
import yaml
import re
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables with validation
INPUT_DIR = os.getenv('INPUT_DIR')
OUTPUT_DIR = os.getenv('OUTPUT_DIR')

if not INPUT_DIR:
    logger.error("Error: INPUT_DIR environment variable is not set.")
    sys.exit(1)
if not OUTPUT_DIR:
    logger.error("Error: OUTPUT_DIR environment variable is not set.")
    sys.exit(1)
if not os.path.isdir(INPUT_DIR):
    logger.error(f"Error: Input directory {INPUT_DIR} does not exist or is not mounted.")
    sys.exit(1)

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

# Specific technology lists for accurate classification
DATABASE_TECHNOLOGIES = ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch']
MESSAGE_QUEUE_TECHNOLOGIES = ['apache kafka', 'rabbitmq', 'activemq', 'zeromq', 'nats', 'pubsub', 'servicebus']
KEY_VAULT_TECHNOLOGIES = ['hashcorp vault']

def standardize_technology(tech):
    """Standardize technology names to their proper casing."""
    tech_lower = tech.lower()
    KNOWN_TECHNOLOGIES = {
        'postgresql': 'PostgreSQL',
        'postgres': 'PostgreSQL',
        'redis': 'Redis',
        'apache kafka': 'Apache Kafka',
        'kafka': 'Apache Kafka',
        'hashcorp vault': 'HashiCorp Vault',
        'vault': 'HashiCorp Vault',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'spring': 'Spring Framework',
        'spring boot': 'Spring Boot',
        'react': 'React',
        'angular': 'Angular',
        'kong': 'Kong',
    }
    return KNOWN_TECHNOLOGIES.get(tech_lower, tech.capitalize())

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

    if entity['type'] == 'service':
        if 'spring' in tech or 'spring boot' in tech:
            tags = ['spring-service']
            entity['technology'] = 'Spring Boot Service'
        elif 'react' in tech:
            tags = ['react']
            entity['technology'] = 'React'
        elif 'angular' in tech:
            tags = ['angular']
            entity['technology'] = 'Angular'
        elif 'kong' in tech:
            tags = ['kong']
            entity['technology'] = 'Kong'
    elif entity['type'] == 'library':
        if 'spring' in tech:
            tags = ['spring-library']
            entity['technology'] = 'Spring Framework'
            if 'database' in description or 'postgres' in description:
                tags.extend(['spring-data', 'database-library'])
                entity['technology'] = 'Spring Data JPA'
        if container_name:
            tags.append(f"{container_name}-library")
    elif entity['type'] in ['database', 'message-queue', 'key-vault', 'infrastructure']:
        entity['technology'] = standardize_technology(tech)

    entity['tags'] = tags
    return entity

def parse_mermaid_file(mmd_file):
    """Parse a Mermaid file to extract entities and relationships."""
    with open(mmd_file, 'r') as f:
        code = f.read().strip()

    lines = code.split('\n')
    entities = {}
    relationships = []
    id_to_key = {}
    stack = []
    current_container = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue

        if line.endswith('{'):
            match = re.match(r'(\w+)\((\w+),\s*"(.+)"\)\s*\{', line)
            if match:
                boundary_type, id, label = match.groups()
                if boundary_type == 'System_Boundary':
                    if ', domain: ' in label:
                        system_name, domain = label.split(', domain: ', 1)
                        system_name = sanitize_name(system_name.strip())
                        domain = sanitize_name(domain.strip())
                    else:
                        system_name = sanitize_name(label)
                        domain = None
                    entity = {
                        'kind': 'system',
                        'name': system_name,
                        'description': '',
                        'domain': domain,
                        'id': id
                    }
                    entities[id] = entity
                    stack.append(entity)
                elif boundary_type == 'Boundary':
                    current_container = sanitize_name(label)
                    stack.append({'type': 'boundary', 'name': current_container})
                continue
        elif line == '}':
            if stack:
                stack.pop()
        else:
            if line.startswith('Person('):
                match = re.match(r'Person\((\w+),\s*"(.+)",\s*"(.+)"\)', line)
                if match:
                    id, name, description = match.groups()
                    name = sanitize_name(name)
                    entity = {
                        'kind': 'user',
                        'name': name,
                        'description': description,
                        'id': id
                    }
                    key = ('user', name)
                    entities[id] = entity
                    id_to_key[id] = key
            elif line.startswith('Container(') or line.startswith('ContainerDb('):
                match = re.match(r'(Container|ContainerDb)\((\w+),\s*"(.+)",\s*"(.+)",\s*"(.+)"\)', line)
                if match:
                    container_type, id, name, technology, description = match.groups()
                    name = sanitize_name(name)
                    kind = 'component' if container_type == 'Container' else 'resource'
                    entity_type = 'service' if container_type == 'Container' else 'database'
                    tech_lower = technology.lower()
                    if tech_lower in INFRA_TECHNOLOGIES or container_type == 'ContainerDb':
                        kind = 'resource'
                        if tech_lower in DATABASE_TECHNOLOGIES:
                            entity_type = 'database'
                        elif tech_lower in MESSAGE_QUEUE_TECHNOLOGIES:
                            entity_type = 'message-queue'
                        elif tech_lower in KEY_VAULT_TECHNOLOGIES:
                            entity_type = 'key-vault'
                        else:
                            entity_type = 'infrastructure'
                    elif tech_lower in ['angular', 'react']:
                        entity_type = 'website'
                    system = next((item['name'] for item in reversed(stack) if item.get('kind') == 'system'), None)
                    entity = {
                        'kind': kind,
                        'name': name,
                        'description': description,
                        'technology': standardize_technology(technology),
                        'type': entity_type,
                        'system': system,
                        'container': current_container if current_container else None,
                        'id': id
                    }
                    if current_container and kind == 'component':
                        entity['type'] = 'library'
                    key = (entity['kind'], entity['name'])
                    entities[id] = entity
                    id_to_key[id] = key
            elif line.startswith('Rel('):
                match = re.match(r'Rel\((\w+),\s*(\w+),\s*"(.+)",\s*"(.+)"\)', line)
                if match:
                    source, target, description, technology = match.groups()
                    source_key = id_to_key.get(source, ('unknown', source))
                    target_key = id_to_key.get(target, ('unknown', target))
                    relationships.append({
                        'source': source_key,
                        'target': target_key,
                        'description': description,
                        'technology': technology.lower()
                    })

    return entities, relationships

def process_relationships(entities, relationships):
    """Process relationships to add dependsOn, providesApis, consumesApis."""
    for rel in relationships:
        source_key = rel['source']
        target_key = rel['target']
        technology = rel['technology']
        description = rel['description']
        if source_key in entities and target_key in entities:
            source = entities[source_key]
            target = entities[target_key]
            if technology in API_TECHNOLOGIES:
                api_name = sanitize_name(f"api-{description}")
                api_key = ('api', api_name)
                api_ref = generate_entity_ref('api', api_name)
                api_type = API_TYPE_MAPPING.get(technology, 'openapi')
                if 'providesApis' not in target:
                    target['providesApis'] = []
                if 'consumesApis' not in source:
                    source['consumesApis'] = []
                if api_ref not in target['providesApis']:
                    target['providesApis'].append(api_ref)
                if api_ref not in source['consumesApis']:
                    source['consumesApis'].append(api_ref)
                api_system = target.get('system')
                api_entity = {
                    'kind': 'api',
                    'name': api_name,
                    'description': description,
                    'technology': technology,
                    'type': api_type,
                    'system': api_system,
                }
                entities[api_key] = api_entity
            else:
                if 'dependsOn' not in source:
                    source['dependsOn'] = []
                dep_ref = generate_entity_ref(target['kind'], target['name'])
                if dep_ref not in source['dependsOn']:
                    source['dependsOn'].append(dep_ref)

def generate_catalog_files():
    """Generate Backstage catalog YAML files from all Mermaid files."""
    mmd_files = list(Path(INPUT_DIR).rglob('*.mmd'))
    if not mmd_files:
        logger.error(f"Error: No .mmd files found in {INPUT_DIR}")
        sys.exit(1)

    all_entities = {}
    all_relationships = []
    for mmd_file in mmd_files:
        entities, relationships = parse_mermaid_file(mmd_file)
        all_relationships.extend(relationships)
        for entity_id, entity in entities.items():
            key = (entity['kind'], entity['name'])
            if key not in all_entities:
                all_entities[key] = entity
            else:
                existing = all_entities[key]
                if len(entity.get('description', '')) > len(existing.get('description', '')):
                    existing['description'] = entity['description']
                if entity.get('technology') and not existing.get('technology'):
                    existing['technology'] = entity['technology']
                if 'domain' in entity and 'domain' not in existing:
                    existing['domain'] = entity['domain']

    process_relationships(all_entities, all_relationships)

    group_name = sanitize_name(TEAM_NAME)
    all_entities[('group', group_name)] = {
        'kind': 'group',
        'name': group_name,
        'description': f"Team {TEAM_NAME}",
        'type': 'team'
    }

    domains = set()
    for (kind, name), entity in all_entities.items():
        if kind == 'system' and entity.get('domain'):
            domains.add(entity['domain'])
    for domain in domains:
        all_entities[('domain', domain)] = {
            'kind': 'domain',
            'name': domain,
            'description': f"Domain for {domain}",
        }

    for (kind, name), entity in all_entities.items():
        container_name = entity.get('container')
        entity = refine_tags_and_technology(entity, container_name)

    for (kind, name), entity in all_entities.items():
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
            'spec': {}
        }

        if entity['kind'] == 'group':
            yaml_data['spec']['type'] = entity.get('type', 'team')
        elif entity['kind'] == 'domain':
            yaml_data['spec']['owner'] = f"group:{group_name}"
        elif entity['kind'] != 'user':
            yaml_data['spec']['owner'] = f"group:{group_name}"
            if entity['kind'] in ['component', 'api', 'resource']:
                yaml_data['spec']['lifecycle'] = LIFECYCLE
            if 'type' in entity:
                yaml_data['spec']['type'] = entity['type']
            if entity['kind'] == 'system' and entity.get('domain'):
                yaml_data['spec']['domain'] = entity['domain']
            if entity['kind'] in ['component', 'resource', 'api'] and entity.get('system'):
                yaml_data['spec']['system'] = entity['system']
            if entity.get('dependsOn'):
                yaml_data['spec']['dependsOn'] = entity['dependsOn']
            if entity.get('providesApis'):
                yaml_data['spec']['providesApis'] = entity['providesApis']
            if entity.get('consumesApis'):
                yaml_data['spec']['consumesApis'] = entity['consumesApis']
            if entity.get('technology') and entity['kind'] != 'api':
                yaml_data['spec']['technology'] = entity['technology']

        with open(output_file, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False)
        logger.info(f"Generated: {output_file}")

if __name__ == "__main__":
    generate_catalog_files()
