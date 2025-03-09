# DrawWard

**WIP**: This project streamlines software architecture design by converting C4 model diagrams created in Draw.io into Backstage catalog files. It bridges architecture prototyping with Backstage’s developer portal, enabling rapid code generation, unified documentation, and a consistent view of your software landscape.

## Intentions

The core goals of this project are:

- **Design with C4 Diagrams**: Prototype your architecture (systems, containers, components) using Draw.io’s C4 model.
- **Generate Backstage Catalog Files**: Convert C4 diagrams into modular `catalog-info.yaml` files for Backstage.
- **Integrate with Backstage**: Import catalog files into Backstage, reflecting systems, services, components, and their relationships.
- **Generate Template Code**: Leverage Backstage’s scaffolding to create boilerplate code from catalog entities.
- **Unified Documentation**: Link architecture with TechDocs imported from the repository.
- **Rapid Prototyping & Consistency**: Accelerate development and maintain an up-to-date architectural overview.

### Future Vision

We plan to integrate Structurizr to dynamically update C4 diagrams from code, generating DSL and live diagrams that reflect the current system state. This is a future enhancement to keep C4 diagrams and catalog entities up to date.

## Prerequisites

- **Tools**:
  - Draw.io with the C4 shape library.
  - Docker for SVG-to-XML conversion.
  - A running Backstage instance.
- **Knowledge**:
  - C4 model basics (system, container, component levels).
  - Backstage catalog and scaffolding features.
  - Software architecture concepts.

## Workflow Overview

1. **Create C4 Diagrams**:
   - Design architecture in Draw.io using C4 shapes.
   - Export as SVG files with embedded XML to `docs/design/drawio/`.

2. **Convert SVG to XML**:
   - Use a Docker-based tool to extract XML, saved to `docs/design/xml/`.

3. **Generate Catalog Files**:
   - Run the enhanced Python script to convert XML into individual Backstage catalog files.
   - Files are organized into `catalog/systems/`, `catalog/components/`, `catalog/resources/`, and `catalog/apis/`, with relationships like dependencies and APIs included.

4. **Import into Backstage**:
   - Backstage automatically imports and validates catalog files from the repository.
   - View systems, services, components, and their dependencies in the UI.
   - **Updating Catalog Files**: Prefer regenerating from diagrams for consistency, but manual edits are possible.

5. **Generate Template Code**:
   - Use Backstage scaffolding to generate code from catalog entities, optionally storing it in this repository.

6. **Import TechDocs**:
   - Import technical documentation into Backstage for a unified view.

## Enhanced XML to Backstage Conversion

The conversion script has been upgraded to align with Backstage best practices:

- **Configurability**: Reads environment variables (`REPO_SLUG`, `TEAM_NAME`, `OWNER`, `LIFECYCLE`) for project-specific settings.
- **Relationship Mapping**: Captures C4 relationships as `dependsOn`, `providesApis`, and `consumesApis` in the catalog files.
- **API Entities**: Creates `API` entities for API interactions (e.g., JSON/HTTP), enhancing service visibility.
- **Modular Files**: Generates one YAML file per entity (e.g., `components/authorization-service.yaml`) for scalability.
- **System Hierarchy**: Links entities to parent systems based on C4 boundaries.
- **Best Practices**: Organizes files into `systems/`, `components/`, `resources/`, and `apis/`, with annotations (e.g., `github.com/project-slug`) and tags.

These improvements make the catalog files more actionable in Backstage, supporting dependency visualization, API management, and service discovery.

## Repository Structure

- `catalog/`: Backstage catalog files in subdirectories:
  - `systems/`: System-level entities (e.g., `authorization-server.yaml`).
  - `components/`: Services and libraries (e.g., `authorization-service.yaml`).
  - `resources/`: Infrastructure (e.g., `database-users-clients.yaml`).
  - `apis/`: API definitions (e.g., `api-oauth2.yaml`).
- `docs/design/drawio/`: C4 diagrams in SVG format.
- `docs/design/xml/`: Temporary XML files.
- `.github/workflows/`: Automation workflows.

## Usage

### Makefile Commands

- `make build-drawio-image`: Build Docker image for SVG-to-XML conversion.
- `make convert-drawio-svg-to-xml`: Convert SVG to XML.
- `make convert-xml-to-backstage-files`: Generate catalog files from XML.
- `make lint-backstage-files`: Lint generated catalog files.
- `make clean`: Remove generated files.
- `make all`: Run the full workflow.

### Backstage Integration Details

- **Catalog Validation**: Backstage validates files on import; errors appear in the UI if validation fails.
- **Repository-Based Import**: Configure Backstage to import catalog files and TechDocs from this repository.

## Future Improvements

- **Dynamic Diagrams**: Use Structurizr for code-to-diagram updates.
- **Automation**: Enhance workflows for specific tasks.
- **Script Features**: Support additional C4 metadata (e.g., more relationship types).
