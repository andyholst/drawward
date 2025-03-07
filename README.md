# DrawWard

**WIP**: This project streamlines software architecture design by using C4 model diagrams in Draw.io to prototype systems, generate Backstage catalog files, and integrate them into Backstage. It enables rapid code generation and unified documentation, bridging architecture and development seamlessly. Updated the xml converter after validation integration with Backstage.

## Intentions

The core goals of this project are:

- **Design with C4 Diagrams**: Create architecture diagrams (system, container, component) in Draw.io to define your software landscape.
- **Generate Backstage Catalog Files**: Convert C4 diagrams into `catalog-info.yaml` files to catalog services, systems, and components in Backstage.
- **Integrate with Backstage**: Import catalog files into Backstage from the repository, providing an up-to-date architectural overview.
- **Generate Template Code**: Use Backstage’s scaffolding feature to produce boilerplate code based on catalog entities, optionally storing it in the same repository.
- **Unified Documentation**: Import TechDocs from the repository into Backstage, linking architecture with technical documentation.
- **Rapid Prototyping & Consistency**: Speed up development with generated code and maintain a consistent view of your architecture in Backstage.

### Future Vision

Looking ahead, we aim to dynamically update C4 diagrams from code using Structurizr. This would involve generating DSL from the codebase and creating live diagrams (not limited to SVG) at different levels (system, container, component), reflecting the current state of the system. This is a future enhancement and not part of the current scope.

## Prerequisites

- **Tools**:
  - Draw.io with the C4 shape library enabled.
  - Docker installed and running.
  - A running Backstage instance.
- **Knowledge**:
  - Basics of the C4 model (system, container, component diagrams).
  - Understanding of Backstage’s catalog and scaffolding features.
  - Familiarity with software architecture concepts.

## Workflow Overview

1. **Create C4 Diagrams**:
   - Design your architecture in Draw.io using C4 diagrams.
   - Export as SVG files with embedded XML metadata to `docs/design/drawio/`.

2. **Convert SVG to XML**:
   - Use a Docker-based converter to extract XML from SVG files, saved to `docs/design/xml/`.

3. **Generate Catalog Files**:
   - Convert XML to Backstage catalog files (`catalog-info.yaml`) using a custom script.
   - Store files in `catalog/` with subdirectories (`system/`, `container/`, `component/`).

4. **Import into Backstage**:
   - Backstage imports and validates catalog files from the repository automatically.
   - View your systems, services, and components in the Backstage UI.
   - **Updating Catalog Files**: While generation from diagrams is preferred, you can manually edit catalog files if needed. To maintain consistency, update diagrams and regenerate files.

5. **Generate Template Code**:
   - Use Backstage’s scaffolding feature to create boilerplate code from catalog entities.
   - Optionally configure to store code in the same repository.

6. **Import TechDocs**:
   - Import technical documentation from the repository into Backstage for a unified view.

## Repository Structure

- `catalog/`: Generated Backstage catalog files (`catalog-info.yaml`) in subdirectories (`system/`, `container/`, `component/`).
- `docs/design/drawio/`: C4 diagrams in SVG format.
- `docs/design/xml/`: Temporary XML files from SVG conversion.
- `.github/workflows/`: Automation workflows for conversion and validation.

## Usage

### Makefile Commands

Manage the workflow with these commands:

- **`make build-drawio-image`**: Builds the Docker image for SVG-to-XML conversion.
- **`make convert-drawio-svg-to-xml`**: Converts SVG files to XML.
- **`make convert-xml-to-backstage-files`**: Converts XML to Backstage catalog files.
- **`make clean`**: Removes generated XML and catalog files.
- **`make all`**: Runs the full workflow (build, SVG-to-XML, XML-to-catalog).

### Backstage Integration Details

- **Catalog Validation**: Backstage validates `catalog-info.yaml` files during import. If validation fails, entities are not added, and errors are logged in the Backstage UI.
- **Repository-Based Import**: Store catalog files and TechDocs in this repository, and configure Backstage to import them automatically.

## Future Improvements

- **Dynamic Diagrams**: Integrate Structurizr to generate DSL from code and update diagrams dynamically.
- **Enhanced Automation**: Add Makefile targets or GitHub Actions for specific tasks.
- **Script Refinement**: Improve the XML-to-YAML conversion to support more C4 metadata.

This project connects C4-based architecture design with Backstage, enabling rapid prototyping, consistent documentation, and streamlined development through code generation and TechDocs integration.
