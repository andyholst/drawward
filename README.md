# DrawWard

**WIP**: This project streamlines software architecture design for **multiple services** by converting C4 model diagrams created in Draw.io and Mermaid diagrams into Backstage catalog files. It bridges architecture prototyping with Backstage’s developer portal, enabling rapid code generation, unified documentation, and a consistent view of your software landscape across services.

## Intentions

The core goals of this project are:

- **Design with C4 and Mermaid Diagrams**: Prototype your architecture for **multiple services** using Draw.io’s C4 model and Mermaid diagrams, organized by service in subdirectories.
- **Generate Backstage Catalog Files**: Convert diagrams into modular, **service-specific** `catalog-info.yaml` files for Backstage.
- **Integrate with Backstage**: Import catalog files into Backstage, reflecting systems, services, components, and their relationships across multiple services.
- **Generate Template Code**: Leverage Backstage’s scaffolding to create boilerplate code from catalog entities.
- **Unified Documentation**: Link architecture with TechDocs imported from the repository.
- **Rapid Prototyping & Consistency**: Accelerate development and maintain an up-to-date architectural overview through automated conversions and validations.

### Future Vision

We plan to integrate Structurizr to dynamically update C4 diagrams from code, generating DSL and live diagrams that reflect the current system state. This is a future enhancement to keep C4 diagrams, Mermaid diagrams, and catalog entities synchronized.

## Prerequisites

- **Tools**:
  - Draw.io with the C4 shape library for creating C4 model diagrams.
  - Mermaid diagramming tool for creating Mermaid diagrams.
  - Docker for SVG-to-XML conversion, XML-to-YAML conversion, Mermaid-to-YAML conversion, linting, and comparison operations.
  - A running Backstage instance to import and utilize the generated catalog files.
- **Knowledge**:
  - Understanding of the C4 model (system, container, component levels).
  - Familiarity with Mermaid syntax for architecture diagrams.
  - Knowledge of Backstage catalog structure, scaffolding features, and TechDocs integration.
  - Basic software architecture concepts.

## Workflow Overview

1. **Create Diagrams**:
   - **Draw.io**: Design architecture using C4 shapes in Draw.io, organizing diagrams by service in `docs/design/drawio/<service-name>/`. Export as SVG files with embedded XML.
   - **Mermaid**: Create architecture diagrams using Mermaid syntax, organizing them by service in `docs/design/mermaid/<service-name>/`.

2. **Convert Diagrams**:
   - **Draw.io**: Extract XML from SVG files into `docs/design/xml/<service-name>/` using a Docker-based tool.
   - **Mermaid**: Convert Mermaid files directly into Backstage YAML files.

3. **Generate Catalog Files**:
   - Use Python scripts (`convert_xml_to_backstage_files.py` for Draw.io, `convert_mermaid_to_backstage_files.py` for Mermaid) or the `drawward-cli` tool to convert XML or Mermaid files into Backstage catalog files. These are organized into `catalog/<service-name>/systems/`, `catalog/<service-name>/components/`, `catalog/<service-name>/resources/`, `catalog/<service-name>/apis/`, `catalog/<service-name>/users/`, `catalog/<service-name>/domains/`, and `catalog/<service-name>/groups/`, including relationships like dependencies (`dependsOn`), provided APIs (`providesApis`), and consumed APIs (`consumesApis`).

4. **Backup and Validate**:
   - Backup existing catalog files to `backup_catalog/<service-name>/` before overwriting.
   - Validate generated files against backups and Backstage standards.

5. **Import into Backstage**:
   - Configure Backstage to import catalog files from `catalog/<service-name>/*.yaml`.
   - View systems, services, components, and their relationships in the Backstage UI.
   - **Updating Catalog Files**: Prefer regenerating from diagrams for consistency, though manual edits are supported.

6. **Generate Template Code**:
   - Use Backstage’s scaffolding feature to generate boilerplate code from catalog entities, optionally storing it in this repository.

7. **Import TechDocs**:
   - Import technical documentation into Backstage for a unified view.

## Enhanced XML and Mermaid to Backstage Conversion

The conversion tools (`convert_xml_to_backstage_files.py`, `convert_mermaid_to_backstage_files.py`, and `drawward-cli`) transform diagrams into Backstage catalog files with these features:

- **Multi-Service Support**: Generates files into service-specific subdirectories (e.g., `catalog/<service-name>/`), enabling scalable management of multiple services.
- **Technology Recognition**: Identifies frontend technologies (e.g., React, Angular) as `website` types with tags (e.g., `react`), backend technologies (e.g., Python, Node.js, Go, Spring) as `service` or `library` types, and infrastructure (e.g., PostgreSQL, Redis, Apache Kafka, HashiCorp Vault) as `resource` types with specific classifications (`database`, `message-queue`, `key-vault`).
- **Group Ownership**: Assigns `owner: group:<team-name>` to entities for organizational context.
- **Domain Extraction**: Parses diagrams to create `Domain` entities (e.g., `security.yaml`) and links systems to domains.
- **Infrastructure Support**: Recognizes infrastructure technologies and assigns appropriate Backstage kinds and types.
- **Boundary Handling**: Processes `SystemScopeBoundary` and `ContainerScopeBoundary` from Draw.io or equivalent Mermaid constructs to link entities to their systems and containers.
- **API System Attribution**: Ties APIs to their provider’s system via `providesApis` and `consumesApis`, supporting API technologies like JSON/HTTP, gRPC, GraphQL, etc.
- **Dynamic Metadata**: Generates `tags` (e.g., `[spring-service]`) and `technology` fields (e.g., `Spring Boot Service`) based on entity type and description.
- **Modular Structure**: Produces one YAML file per entity, organized by service and type (e.g., `systems/`, `components/`, `resources/`, `apis/`, `users/`, `domains/`, `groups/`).
- **Configurability**: Reads environment variables (`REPO_SLUG`, `TEAM_NAME`, `OWNER`, `LIFECYCLE`) to customize annotations (`github.com/project-slug`), ownership, and lifecycle stages.

These enhancements ensure catalog files are detailed, actionable, and aligned with Backstage best practices.

## Repository Structure

- `catalog/<service-name>/`: Contains service-specific catalog files:
  - `systems/`: System-level entities (e.g., `authorization-server.yaml`).
  - `components/`: Services and libraries (e.g., `authorization-service.yaml`).
  - `resources/`: Infrastructure (e.g., `postgres-database.yaml`).
  - `apis/`: API definitions (e.g., `api-oauth2.yaml`).
  - `users/`: User entities (e.g., `person.yaml`).
  - `domains/`: Domain entities (e.g., `security.yaml`).
  - `groups/`: Group entities (e.g., `dev-team.yaml`).
- `docs/design/drawio/<service-name>/`: C4 diagrams in SVG format for each service.
- `docs/design/xml/<service-name>/`: Temporary XML files extracted from Draw.io SVGs.
- `docs/design/mermaid/<service-name>/`: Mermaid diagrams for each service.
- `backup_catalog/<service-name>/`: Backups of committed catalog files, mirroring the `catalog/` structure.
- `docker-files/`: Contains Docker build directories:
  - `drawio-converter/`: Dockerfile and scripts for SVG-to-XML conversion.
  - `backstage-converter/`: Dockerfile and Python script for XML-to-YAML conversion.
  - `backstage-entity-validator/`: Dockerfile for linting YAML files.
  - `backstage-compare/`: Dockerfile and script for comparing catalog files.
  - `drawward-cli/`: Dockerfile and scripts for the Drawward CLI tool.
  - `mermaid-converter/`: Unused legacy directory.
  - `mermaid-to-backstage-converter/`: Dockerfile and script for Mermaid-to-YAML conversion.
- `.github/workflows/`: Automation workflows (e.g., CI/CD pipelines).

## Usage

### Drawward CLI

The `drawward-cli` tool is a command-line interface that streamlines generating Backstage catalog files from Draw.io SVG diagrams, with additional support for multi-service workflows.

#### Purpose and Functionality

It automates the conversion of C4 model diagrams into Backstage-compatible YAML files, processing multiple services by scanning subdirectories in a specified input directory and outputting files to a structured output directory. It integrates with Docker for consistency and is fully supported by Makefile commands.

#### Mandatory Requirements

- **Docker Installed and Running**: Required for building and running all Docker images (`drawio-converter`, `backstage-converter`, `backstage-lint`, `backstage-compare`, `drawward-cli`, `mermaid-to-backstage-converter`).
- **SVG Diagrams Prepared**: C4 model diagrams must be exported as SVG files with embedded XML, organized by service in `docs/design/drawio/<service-name>/`.
- **Mermaid Diagrams Prepared**: Mermaid files must be organized by service in `docs/design/mermaid/<service-name>/`.
- **Docker Images Built**: Build necessary images using Makefile commands (e.g., `make build-drawward-cli-image`, `make build-mermaid-backstage-converter-image`).

#### Running the Tool

- **`make run-drawward-cli`**: Processes all services in `docs/design/drawio/` and generates catalog files in `catalog/`.

#### Customizing Directories

- **Default Directories**:
  - `INPUT_DIR`: `docs/design/drawio` (Draw.io input).
  - `OUTPUT_DIR`: `catalog` (output for both Draw.io and Mermaid).
  - `MERMAID_DIR`: `docs/design/mermaid` (Mermaid input).
  - `DRAWIO_XML_DIR`: `docs/design/xml` (temporary XML storage).
  - `BACKUP_CATALOG_DIR`: `backup_catalog` (backup storage).
- **Custom Input and Output**:
  - Command: `make run-drawward-cli INPUT_DIR=/custom/input OUTPUT_DIR=/custom/output`
  - Effect: Processes Draw.io files from `/custom/input/` to `/custom/output/<service-name>/`.
- **Custom Input Only**:
  - Command: `make run-drawward-cli INPUT_DIR=/custom/input`
  - Effect: Uses `/custom/input/` for input and `catalog/` for output.
- **Dynamic Service Detection**: Automatically detects services from subdirectories in `INPUT_DIR` or `MERMAID_DIR`.

#### Customizing Environment Variables

Set these variables to customize metadata:
- `REPO_SLUG`: Repository slug (default: `myorg/myrepo`), used in annotations like `github.com/project-slug`.
- `TEAM_NAME`: Team name (default: `dev-team`), used for ownership (e.g., `group:dev-team`).
- `OWNER`: Entity owner (default: matches `TEAM_NAME`).
- `LIFECYCLE`: Lifecycle stage (default: `experimental`), applied to components, APIs, and resources.
- **Usage**: `REPO_SLUG=myorg/myproject TEAM_NAME=ops-team LIFECYCLE=production make run-drawward-cli`

#### Advanced Usage: Direct Docker Run

- Draw.io: `docker run --rm -v /path/to/drawio:/input -v /path/to/output:/output drawward-cli convert-svg-to-yaml`
- Mermaid: `docker run --rm -v /path/to/mermaid:/input -v /path/to/output:/output mermaid-to-backstage-converter`

### Makefile Commands

The Makefile provides a comprehensive set of commands to manage the entire workflow. Below is the complete list, ensuring every target is documented:

#### Building Docker Images

- **`make build-drawio-converter-image`**:
  - Builds the `drawio-converter` image from `docker-files/drawio-converter/`.
  - Used for SVG-to-XML conversion.
- **`make build-backstage-converter-image`**:
  - Builds the `backstage-converter` image from `docker-files/backstage-converter/`.
  - Used for XML-to-YAML conversion.
- **`make build-backstage-lint-image`**:
  - Builds the `backstage-lint` image from `docker-files/backstage-entity-validator/`.
  - Used for linting YAML files.
- **`make build-backstage-compare-image`**:
  - Builds the `backstage-compare` image from `docker-files/backstage-compare/`.
  - Used for comparing generated and backup catalog files.
- **`make build-drawward-cli-image`**:
  - Copies scripts from `drawio-converter` and `backstage-converter`, then builds the `drawward-cli` image from `docker-files/drawward-cli/`.
  - Used for end-to-end Draw.io processing.
- **`make build-mermaid-backstage-converter-image`**:
  - Builds the `mermaid-to-backstage-converter` image from `docker-files/mermaid-to-backstage-converter/`.
  - Used for Mermaid-to-YAML conversion.

#### Processing Draw.io Diagrams (Service-Specific)

- **`make convert-drawio-svg-to-xml-%`**:
  - Converts SVG files to XML for a specific service (e.g., `make convert-drawio-svg-to-xml-my-service`).
  - Input: `docs/design/drawio/<service-name>/`.
  - Output: `docs/design/xml/<service-name>/`.
- **`make convert-xml-to-backstage-files-%`**:
  - Converts XML to Backstage YAML for a specific service.
  - Input: `docs/design/xml/<service-name>/`.
  - Output: `catalog/<service-name>/`.
- **`make lint-backstage-files-%`**:
  - Lints YAML files for a specific service in `catalog/<service-name>/`.
- **`make backup-catalogs-%`**:
  - Backs up catalog files for a specific service from `catalog/<service-name>/` to `backup_catalog/<service-name>/`.
- **`make validate-catalogs-%`**:
  - Validates generated YAML files for a specific service against backups in `backup_catalog/<service-name>/`.
- **`make generate-backstage-files-%`**:
  - Generates Backstage YAML files for a specific service using Drawward CLI (e.g., `make generate-backstage-files-my-service`).
  - Input: `docs/design/drawio/<service-name>/`.
  - Output: `catalog/<service-name>/`.

#### Processing Mermaid Diagrams

- **`make convert-mermaid-to-backstage`**:
  - Converts Mermaid files to Backstage YAML for all services listed in `MERMAID_SERVICES` (subdirectories of `docs/design/mermaid/`).
  - Output: `catalog/<service-name>/`.
- **`make convert-mermaid-to-backstage-%`**:
  - Converts Mermaid files to Backstage YAML for a specific service (e.g., `make convert-mermaid-to-backstage-my-service`).
  - Input: `docs/design/mermaid/<service-name>/`.
  - Output: `catalog/<service-name>/`.

#### Integrated Operations

- **`make process-all-common-steps`**:
  - Default target that processes all Draw.io services listed in `SERVICES` (subdirectories of `docs/design/drawio/`).
  - Steps: Backup, SVG-to-XML, XML-to-YAML, linting, validation.
- **`make process-all-steps-with-drawward-cli`**:
  - Runs the complete pipeline for all services using Drawward CLI: `backup-all-catalogs`, `run-drawward-cli`, `validate-all-catalogs`.
- **`make process-and-compare-mermaid-all`**:
  - Runs the full Draw.io pipeline (`process-all-common-steps`), then generates Mermaid YAML files (`convert-mermaid-to-backstage`), and validates against the original backups (`validate-all-catalogs`).
- **`make run-drawward-cli`**:
  - Executes Drawward CLI to generate catalog files for all services in `docs/design/drawio/`, looping through each service in `SERVICES`.

#### Utility Commands

- **`make backup-all-catalogs`**:
  - Backs up catalog files for all services in `SERVICES` from `catalog/` to `backup_catalog/`.
- **`make validate-all-catalogs`**:
  - Validates generated catalog files for all services in `SERVICES` against backups in `backup_catalog/`.
- **`make clean`**:
  - Removes all generated files: `docs/design/xml/`, `catalog/`, and `backup_catalog/`.

#### Service-Specific Processing

- The `$(SERVICES)` target dynamically processes each service in `docs/design/drawio/` with the sequence: `backup-catalogs-%`, `convert-drawio-svg-to-xml-%`, `convert-xml-to-backstage-files-%`, `lint-backstage-files-%`, `validate-catalogs-%`.

### Mermaid Support

- **File Location**: Mermaid diagrams are stored in `docs/design/mermaid/<service-name>/`.
- **Conversion**: Use `make convert-mermaid-to-backstage` for all services or `make convert-mermaid-to-backstage-%` for a specific service.
- **Integrated Workflow**: `make process-and-compare-mermaid-all` backs up committed files, processes Draw.io diagrams, generates Mermaid YAML files (overwriting Draw.io output), and compares against the original backups.

### Backup and Validation Processes

- **Backup**: Before processing, catalog files are copied from `catalog/<service-name>/` to `backup_catalog/<service-name>/` using `make backup-catalogs-%` or `make backup-all-catalogs`. This preserves committed files for validation.
- **Validation**: Generated files are compared to backups using `make validate-catalogs-%` or `make validate-all-catalogs`, ensuring consistency with committed versions. The `backstage-compare` image sorts lists (e.g., `dependsOn`, `providesApis`) to ignore order differences.

## Backstage Integration Details

- **Catalog Import**: Configure Backstage to import from `catalog/<service-name>/*.yaml`.
- **Catalog Validation**: Errors appear in the Backstage UI on import; pre-validate with `make validate-all-catalogs`.
- **Repository-Based Import**: Import catalog files and TechDocs directly from this repository.

## Future Improvements

- **Dynamic Diagrams**: Integrate Structurizr for code-to-diagram updates.
- **Service Automation**: Enhance dynamic service detection and processing.
- **Tool Integrations**: Expand support for additional diagramming tools or converters.
- **Validation Enhancements**: Improve comparison logic for complex YAML structures.
