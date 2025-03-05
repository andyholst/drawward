# C4-to-Backstage Workflow

This is a markdown code block describing a workflow to design software systems using C4 diagrams in Draw.io, convert them into Backstage catalog files, and generate template code for services and microservices. Below is a detailed explanation of the process.

## Overview

The workflow leverages the **C4 model** to create architectural diagrams at different levels (system, container, component) using **Draw.io**. These diagrams are exported as SVG files, processed to extract XML data, and then converted into **Backstage catalog files** (e.g., `catalog-info.yaml`). Finally, **Backstage’s scaffolding feature** generates template code based on the catalog entities, enabling rapid prototyping and consistent architectural documentation.

### Key Benefits

- **Rapid Prototyping**: Quickly turn diagrams into service code.
- **Architectural Consistency**: Maintain an overview in Backstage.
- **Streamlined Development**: Generate boilerplate code to speed up onboarding and coding.

## Prerequisites

- **Tools**:
  - Draw.io with the C4 shape library enabled.
  - Docker installed and running.
  - A running Backstage instance.
- **Knowledge**:
  - Basics of the C4 model (system, container, component diagrams).
  - Understanding of Backstage’s catalog structure and scaffolding feature.
  - Familiarity with software architecture concepts.

## Step-by-Step Process

### Step 1: Create C4 Diagrams in Draw.io

1. Open **Draw.io** and enable the C4 shape library:
   - Go to `Extras` > `Edit Diagram` > Add C4 shapes.
2. Design your architecture:
   - **System Diagram**: High-level view of systems and their relationships.
   - **Container Diagram**: Services or applications within a system.
   - **Component Diagram**: Internal components of a container.
3. Export each diagram as an SVG:
   - Go to `File` > `Export As` > `SVG`.
   - Use default settings to include embedded XML metadata.
4. Save the SVG files in a directory, e.g., `docs/design/drawio/`.

### Step 2: Convert SVG to XML

This step uses a **Makefile** and a **Docker-based converter** to extract XML data from SVG files.

#### Prerequisites

- Docker installed and running.
- SVG files saved in `docs/design/drawio/`.

#### Commands

1. **Build the Docker Image**:
   - Command: `make build-drawio-image`
   - Builds a Docker image named `drawio-converter` using a Dockerfile.
2. **Convert SVG to XML**:
   - Command: `make convert-drawio-svg-to-xml`
   - Extracts XML from SVG files and saves them in `docs/design/xml/`.
3. **Run Both Steps Together**:
   - Command: `make`
   - Combines the build and conversion steps.
4. **Verify Output**:
   - Check the `docs/design/xml/` directory for generated XML files.

### Step 3: Generate Backstage Catalog Files

Convert the XML files into Backstage catalog files (`catalog-info.yaml`).

#### Prerequisites

- XML files in `docs/design/xml/`.
- A script (e.g., in Python or Node.js) to parse XML and generate YAML.

#### Steps

1. **Parse XML**:
   - Use a custom script to extract C4 elements (systems, containers, components).
2. **Map to Backstage Entities**:
   - **C4 System** → `kind: System`
   - **C4 Container** → `kind: Component` (for services)
   - **C4 Component** → `kind: Component` (e.g., `type: library`) or `kind: Resource` (e.g., `type: database`)
3. **Save YAML Files**:
   - Store the generated `catalog-info.yaml` files in a directory, e.g., `catalog/`.

#### Repository Integration

The generated diagrams and Backstage catalog files can be stored in a repository (e.g., GitHub, GitLab) for version control and team collaboration. Backstage supports importing these files directly from a repository to keep the catalog current. Additionally, template code can be generated into the same repository, ensuring all artifacts—diagrams, catalog files, and code—remain connected in a unified environment.

### Step 4: Import into Backstage

1. Move the `catalog-info.yaml` files to your Backstage instance’s catalog directory (e.g., `/catalog-info`), or rely on repository integration for automatic imports.
2. Start Backstage locally or deploy it.
3. Verify the catalog in the Backstage UI to see your systems, services, and components.

### Step 5: Generate Code Templates

1. Define scaffolding templates in Backstage for code generation.
2. Use the Backstage UI to select a template and generate code.
3. The output is a new repository or local folder with boilerplate code, optionally integrated into the same repository as your diagrams and catalog files.

## Future Improvements

- Add Makefile targets like `generate-catalog` or `clean`.
- Replace the Docker-based converter with a script if SVG formats change.
- Enhance the XML-to-YAML script to support additional C4 elements or metadata.

This workflow streamlines the process from architecture design to code generation, integrating C4 diagrams with Backstage effectively while supporting repository-based collaboration.
