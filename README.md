# DrawWard

**WIP**: This project streamlines software architecture design for **multiple services** by converting C4 model diagrams created in Draw.io into Backstage catalog files. It bridges architecture prototyping with Backstage’s developer portal, enabling rapid code generation, unified documentation, and a consistent view of your software landscape across services.

## Intentions

The core goals of this project are:

- **Design with C4 Diagrams**: Prototype your architecture for **multiple services** using Draw.io’s C4 model, organizing diagrams by service in subdirectories.
- **Generate Backstage Catalog Files**: Convert C4 diagrams into modular, **service-specific** `catalog-info.yaml` files for Backstage.
- **Integrate with Backstage**: Import catalog files into Backstage, reflecting systems, services, components, and their relationships across multiple services.
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
   - Design architecture in Draw.io using C4 shapes, organizing diagrams by service in `docs/design/drawio/<service-name>/`.
   - Export as SVG files with embedded XML.

2. **Convert SVG to XML**:
   - Use a Docker-based tool to extract XML, saved to `docs/design/xml/<service-name>/`.

3. **Generate Catalog Files**:
   - Use the enhanced Python script (`convert_xml_to_backstage_files.py`) or the new `drawward-cli` tool to convert XML into individual Backstage catalog files, organized into `catalog/<service-name>/systems/`, `catalog/<service-name>/components/`, `catalog/<service-name>/resources/`, and `catalog/<service-name>/apis/`, with relationships like dependencies and APIs included.

4. **Import into Backstage**:
   - Configure Backstage to import catalog files from service-specific subdirectories (e.g., `catalog/<service-name>/*.yaml`).
   - View systems, services, components, and their dependencies in the UI.
   - **Updating Catalog Files**: Prefer regenerating from diagrams for consistency, but manual edits are possible.

5. **Generate Template Code**:
   - Use Backstage scaffolding to generate code from catalog entities, optionally storing it in this repository.

6. **Import TechDocs**:
   - Import technical documentation into Backstage for a unified view.

## Enhanced XML to Backstage Conversion

The `convert_xml_to_backstage_files.py` script and the new `drawward-cli` tool transform C4 model diagrams from Draw.io into Backstage catalog files with these features:

- **Multi-Service Support**: Generates catalog files into service-specific subdirectories (e.g., `catalog/<service-name>/`), enabling scalable management of multiple services.
- **Technology Recognition**: Identifies frontend technologies like React and Angular as `website` types with tags (e.g., `react-frontend`), alongside Python, Node.js, Go, and Spring services/libraries.
- **Group Ownership**: Assigns `owner: group:<team-name>` to entities for better organizational context.
- **Domain Extraction**: Parses C4 diagrams to create `Domain` entities (e.g., `security.yaml`) and links systems to domains.
- **Infrastructure Support**: Recognizes infrastructure technologies (e.g., PostgreSQL, Redis, Apache Kafka, HashiCorp Vault) as `Resource` kinds, assigning types like `database`, `message-queue`, or `key-vault`.
- **Boundary Handling**: Processes `SystemScopeBoundary` and `ContainerScopeBoundary` to link entities to their systems and containers.
- **API System Attribution**: Ties APIs to their provider’s system via `providesApis` and `consumesApis`.
- **Dynamic Metadata**: Generates tags and `technology` fields based on entity type and description (e.g., `tags: [spring-service]`, `technology: Spring Boot Service`).
- **Modular Structure**: Produces one YAML file per entity, organized by service and type.
- **Configurability**: Reads environment variables (`REPO_SLUG`, `TEAM_NAME`, `OWNER`, `LIFECYCLE`) to customize annotations and ownership.

These enhancements ensure catalog files are detailed, actionable, and aligned with Backstage best practices.

## Repository Structure

- `catalog/<service-name>/`: Contains subdirectories for each service’s catalog files:
  - `systems/`: System-level entities (e.g., `authorization-server.yaml`).
  - `components/`: Services and libraries (e.g., `authorization-service.yaml`).
  - `resources/`: Infrastructure (e.g., `postgres-database.yaml`).
  - `apis/`: API definitions (e.g., `api-oauth2.yaml`).
- `docs/design/drawio/<service-name>/`: C4 diagrams in SVG format for each service.
- `docs/design/xml/<service-name>/`: Temporary XML files for each service.
- `.github/workflows/`: Automation workflows.

## Usage

The `drawward-cli` tool is a command-line interface designed to streamline the generation of Backstage catalog files from Draw.io SVG diagrams in the DrawWard project. It simplifies the process by providing a single interface to convert SVG files (containing C4 model diagrams) into YAML catalog files, leveraging Docker for consistency and integrating seamlessly with Makefile commands.

### Purpose and Functionality

The tool automates the conversion of architecture diagrams into Backstage-compatible catalog files, enabling users to maintain a consistent view of their software landscape. It processes multiple services by scanning subdirectories in a specified input directory, generating catalog files for each service, and outputting them to a designated directory structure. This makes it ideal for managing complex, multi-service architectures.

### Mandatory Requirements

To use `drawward-cli` effectively, ensure the following prerequisites are met:
1. **Docker Installed and Running**: Docker is essential for building and running the `drawward-cli` image.
2. **SVG Diagrams Prepared**: C4 model diagrams must be exported as SVG files (with embedded XML) and organized by service in subdirectories (e.g., `docs/design/drawio/<service-name>/` by default).
3. **Docker Image Built**: Build the `drawward-cli` image locally using the provided Makefile command (e.g., `make build-drawio-image`). This is a one-time step unless the Dockerfile changes.

### Running the Tool

The tool can be executed via Makefile commands, which handle input and output directory mappings automatically. Key commands include:
- **`make run-drawward-cli`**: Processes all services in the input directory and generates catalog files in the output directory.

These commands use default directories unless overridden:
- **Default Input Directory (`INPUT_DIR`)**: `docs/design/drawio`
- **Default Output Directory (`OUTPUT_DIR`)**: `catalog`

### Customizing Input and Output Directories

Users can override the default directories by setting `INPUT_DIR` and `OUTPUT_DIR` when running Makefile commands. This allows for flexible workflows:
- **Custom Input and Output**:
  - Command: `make run-drawward-cli INPUT_DIR=/custom/input OUTPUT_DIR=/custom/output`
  - Effect: Processes services from `/custom/input/` and outputs to `/custom/output/<service-name>/`.
- **Custom Input Only**:
  - Command: `make run-drawward-cli INPUT_DIR=/custom/input`
  - Effect: Uses `/custom/input/` for input and the default `catalog/` for output.
- **Dynamic Service Detection**: The tool automatically detects services from subdirectories in `INPUT_DIR`, so no manual service listing is required.

### Customizing Environment Variables

Optional environment variables can be set to customize metadata in the generated catalog files:
- `REPO_SLUG`: Repository identifier (default: `myorg/myrepo`).
- `TEAM_NAME`: Team name for ownership (default: `dev-team`).
- `OWNER`: Entity owner (default: matches `TEAM_NAME`).
- `LIFECYCLE`: Lifecycle stage (default: `experimental`).
- **Usage**: Set before the command, e.g., `REPO_SLUG=myorg/myproject TEAM_NAME=ops-team make run-drawward-cli`.

### Advanced Usage: Direct Docker Run

For advanced users, the Docker container can be run directly, manually specifying input and output directories:
- Command: `docker run --rm -v /path/to/input:/input -v /path/to/output:/output drawward-cli convert-svg-to-yaml`
- This processes SVG files from `/path/to/input` and outputs YAML to `/path/to/output`.

### Default Behavior

If no custom directories are specified, `drawward-cli` uses:
- **Input**: `docs/design/drawio/<service-name>/`
- **Output**: `catalog/<service-name>/`
This ensures the tool works out of the box with the default repository structure while allowing customization for different setups.

### Makefile Commands

- **`make build-drawio-image`**: Builds the Docker image used for SVG-to-XML conversion.
- **`make convert-drawio-svg-to-xml`**: Converts SVG files to XML for all services in `docs/design/drawio/`.
- **`make convert-xml-to-backstage-files`**: Generates Backstage catalog files from XML for all services using the Python script.
- **`make lint-backstage-files`**: Lints generated catalog files to ensure they meet Backstage standards.
- **`make clean`**: Removes generated files (e.g., XML and catalog files) to reset the workspace.
- **`make all`**: Runs the full workflow (SVG-to-XML conversion and catalog file generation) for all services in `docs/design/drawio/`. Service-specific processing is a future enhancement.
- **`make generate-backstage-files-%`**: Generates catalog files for a specific service (e.g., `make generate-backstage-files-my-service` processes `docs/design/drawio/my-service/`).
- **`make run-drawward-cli`**: Executes the `drawward-cli` tool to generate catalog files for all services in one command, simplifying the process.
- **`make backup-all-catalogs`**: Creates backups of all existing catalog files before regeneration, ensuring data safety.
- **`make validate-all-catalogs`**: Validates all generated catalog files against Backstage schema requirements.
- **`make process-all-steps-with-drawward-cli`**: Runs the complete pipeline using `drawward-cli`, including backup, catalog file generation, and validation in a single command.

These commands provide flexibility, allowing users to process all services or target specific ones, while the `drawward-cli`-specific commands offer a streamlined, end-to-end experience.

### Backstage Integration Details

- **Catalog Import**: Configure Backstage to import from `catalog/<service-name>/*.yaml`.
- **Catalog Validation**: Backstage validates files on import; errors appear in the UI.
- **Repository-Based Import**: Import catalog files and TechDocs from this repository.

## Future Improvements

- **Dynamic Diagrams**: Use Structurizr for code-to-diagram updates.
- **Service Automation**: Automate detection and processing of new services.
- **Tool Integrations**: Expand integrations with additional tools, including potential enhancements to `drawward-cli`.
- **Service-Specific Processing**: Enhance Makefile targets to process individual services more seamlessly.
