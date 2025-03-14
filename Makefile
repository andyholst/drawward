SHELL := /bin/bash

DRAWIO_CONVERTER_IMAGE := drawio-converter
DRAWIO_CONVERTER_BUILD_DIR := docker-files/drawio-converter
DRAWIO_BASE_DIR := docs/design/drawio
DRAWIO_XML_DIR := docs/design/xml
BACKSTAGE_CONVERTER_IMAGE := backstage-converter
BACKSTAGE_CONVERTER_BUILD_DIR := docker-files/backstage-converter
BACKSTAGE_LINT_IMAGE := backstage-lint
BACKSTAGE_LINT_BUILD_DIR := docker-files/backstage-entity-validator
BACKUP_CATALOG_DIR := backup_catalog
CATALOG_DIR := catalog

DRAWWARD_CLI_IMAGE := drawward-cli
DRAWWARD_CLI_BUILD_DIR := docker-files/drawward-cli

REPO_SLUG ?= myorg/myrepo
TEAM_NAME ?= dev-team
OWNER ?= $(TEAM_NAME)
LIFECYCLE ?= experimental

# Overridable input and output directories
INPUT_DIR ?= $(DRAWIO_BASE_DIR)
OUTPUT_DIR ?= $(CATALOG_DIR)

# Dynamically scan services from INPUT_DIR
SERVICES := $(notdir $(wildcard $(INPUT_DIR)/*))

.PHONY: process-all-common-steps build-drawio-converter-image build-backstage-converter-image build-backstage-lint-image build-drawward-cli-image run-drawward-cli clean process-all-steps-with-drawward-cli backup-all-catalogs validate-all-catalogs $(SERVICES)

# Default target: process all services with the original steps
process-all-common-steps: $(SERVICES)

build-drawio-converter-image:
		@docker build -t $(DRAWIO_CONVERTER_IMAGE) $(DRAWIO_CONVERTER_BUILD_DIR) || { echo "Failed to build drawio-converter image"; exit 1; }
		@echo "Docker image $(DRAWIO_CONVERTER_IMAGE) built successfully"

build-backstage-converter-image:
		@docker build -t $(BACKSTAGE_CONVERTER_IMAGE) $(BACKSTAGE_CONVERTER_BUILD_DIR) || { echo "Failed to build backstage-converter image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_CONVERTER_IMAGE) built successfully"

build-backstage-lint-image:
		@docker build -t $(BACKSTAGE_LINT_IMAGE) $(BACKSTAGE_LINT_BUILD_DIR) || { echo "Failed to build backstage-lint image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_LINT_IMAGE) built successfully"

copy-scripts-to-drawward-cli:
		@cp $(DRAWIO_CONVERTER_BUILD_DIR)/convert_svg_to_xml.sh $(DRAWWARD_CLI_BUILD_DIR)/
		@cp $(BACKSTAGE_CONVERTER_BUILD_DIR)/convert_xml_to_backstage_files.py $(DRAWWARD_CLI_BUILD_DIR)/

build-drawward-cli-image: copy-scripts-to-drawward-cli
		@docker build -t $(DRAWWARD_CLI_IMAGE) $(DRAWWARD_CLI_BUILD_DIR) || { echo "Failed to build drawward-cli image"; exit 1; }
		@echo "Docker image $(DRAWWARD_CLI_IMAGE) built successfully"

# Parameterized target for each service
$(SERVICES): %: backup-catalogs-% convert-drawio-svg-to-xml-% convert-xml-to-backstage-files-% lint-backstage-files-% validate-catalogs-%

convert-drawio-svg-to-xml-%: build-drawio-converter-image
		@mkdir -p $(DRAWIO_XML_DIR)/$*
		@echo "Converting SVG to XML for service $*"
		@docker run --rm \
				-v "$(PWD)/$(INPUT_DIR)/$*:/input" \
				-v "$(PWD)/$(DRAWIO_XML_DIR)/$*:/output" \
				-e SVG_DIR="/input" \
				-e XML_DIR="/output" \
				$(DRAWIO_CONVERTER_IMAGE) || { echo "Failed to convert SVG files to XML for $*"; exit 1; }
		@echo "SVG files for $* converted to XML in $(DRAWIO_XML_DIR)/$*"

# Convert XML to Backstage files for a specific service
convert-xml-to-backstage-files-%: build-backstage-converter-image
		@mkdir -p $(OUTPUT_DIR)/$*/systems $(OUTPUT_DIR)/$*/components $(OUTPUT_DIR)/$*/resources $(OUTPUT_DIR)/$*/users $(OUTPUT_DIR)/$*/apis
		@echo "Converting XML to Backstage files for service $*"
		@docker run --rm \
				-v "$(PWD)/$(DRAWIO_XML_DIR)/$*:/input" \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/output" \
				-e INPUT_DIR="/input" \
				-e OUTPUT_DIR="/output" \
				-e REPO_SLUG=$(REPO_SLUG) \
				-e TEAM_NAME=$(TEAM_NAME) \
				-e OWNER=$(OWNER) \
				-e LIFECYCLE=$(LIFECYCLE) \
				$(BACKSTAGE_CONVERTER_IMAGE) || { echo "Failed to convert XML files to Backstage YAML for $*"; exit 1; }
		@echo "XML files for $* converted to Backstage YAML in $(OUTPUT_DIR)/$*"

# Lint Backstage files
lint-backstage-files-%: build-backstage-lint-image
		@echo "Linting Backstage files for service $*"
		@docker run --rm \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/app" \
				$(BACKSTAGE_LINT_IMAGE) || { echo "Backstage YAML linting failed for $*"; exit 1; }
		@echo "Backstage YAML files for $* linted successfully"

# Backup catalogs
backup-catalogs-%:
		@mkdir -p $(BACKUP_CATALOG_DIR)/$*/apis $(BACKUP_CATALOG_DIR)/$*/components $(BACKUP_CATALOG_DIR)/$*/resources $(BACKUP_CATALOG_DIR)/$*/systems $(BACKUP_CATALOG_DIR)/$*/users
		@cp -r $(OUTPUT_DIR)/$*/apis/*.yaml $(BACKUP_CATALOG_DIR)/$*/apis/ 2>/dev/null || echo "No API files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/components/*.yaml $(BACKUP_CATALOG_DIR)/$*/components/ 2>/dev/null || echo "No component files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/resources/*.yaml $(BACKUP_CATALOG_DIR)/$*/resources/ 2>/dev/null || echo "No resource files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/systems/*.yaml $(BACKUP_CATALOG_DIR)/$*/systems/ 2>/dev/null || echo "No system files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/users/*.yaml $(BACKUP_CATALOG_DIR)/$*/users/ 2>/dev/null || echo "No user files to backup for $*"

# Validate catalogs
validate-catalogs-%:
		@BACKUP_CATALOG_DIR="$(BACKUP_CATALOG_DIR)/$*" BACKSTAGE_CATALOG_DIR="$(OUTPUT_DIR)/$*" bash compare_catalogs.sh || { echo "Catalog validation failed for $*"; exit 1; }
		@echo "Catalog validation completed successfully for $*"

# Unified SVG to Backstage YAML generation using drawward-cli for a specific service
generate-backstage-files-%: build-drawward-cli-image
		@mkdir -p $(OUTPUT_DIR)/$*/systems $(OUTPUT_DIR)/$*/components $(OUTPUT_DIR)/$*/resources $(OUTPUT_DIR)/$*/users $(OUTPUT_DIR)/$*/apis
		@echo "Generating Backstage YAML files from SVG for service $*"
		@docker run --rm \
				-v "$(PWD)/$(INPUT_DIR)/$*:/input" \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/output" \
				-e REPO_SLUG=$(REPO_SLUG) \
				-e TEAM_NAME=$(TEAM_NAME) \
				-e OWNER=$(OWNER) \
				-e LIFECYCLE=$(LIFECYCLE) \
				$(DRAWWARD_CLI_IMAGE) convert-svg-to-yaml || { echo "Failed to generate Backstage YAML for $*"; exit 1; }
		@echo "Backstage YAML files for $* generated in $(OUTPUT_DIR)/$*"

# Unified SVG to Backstage YAML generation for all services using drawward-cli
run-drawward-cli: build-drawward-cli-image
		@echo "Running drawward-cli for all services in $(INPUT_DIR)"
		@for service in $(SERVICES); do \
				echo "Processing service: $$service"; \
				mkdir -p $(OUTPUT_DIR)/$$service/systems $(OUTPUT_DIR)/$$service/components $(OUTPUT_DIR)/$$service/resources $(OUTPUT_DIR)/$$service/users $(OUTPUT_DIR)/$$service/apis; \
				docker run --rm \
						-v "$(PWD)/$(INPUT_DIR)/$$service:/input" \
						-v "$(PWD)/$(OUTPUT_DIR)/$$service:/output" \
						-e REPO_SLUG=$(REPO_SLUG) \
						-e TEAM_NAME=$(TEAM_NAME) \
						-e OWNER=$(OWNER) \
						-e LIFECYCLE=$(LIFECYCLE) \
						$(DRAWWARD_CLI_IMAGE) convert-svg-to-yaml || { echo "Failed to generate Backstage YAML for $$service"; exit 1; }; \
		echo "Backstage YAML files for $$service generated in $(OUTPUT_DIR)/$$service"; \
		done
		@echo "drawward-cli execution completed for all services"

# Backup all catalogs
backup-all-catalogs:
		@for service in $(SERVICES); do \
				$(MAKE) backup-catalogs-$$service; \
		done

# Validate all catalogs
validate-all-catalogs:
		@for service in $(SERVICES); do \
				$(MAKE) validate-catalogs-$$service; \
		done

# Full pipeline: backup, generate with drawward-cli, validate
process-all-steps-with-drawward-cli: backup-all-catalogs run-drawward-cli validate-all-catalogs

# Clean up generated files
clean:
		@rm -rf $(DRAWIO_XML_DIR) $(OUTPUT_DIR) $(BACKUP_CATALOG_DIR)
		@echo "Cleaned up $(DRAWIO_XML_DIR) and $(OUTPUT_DIR)"

# Catch-all target to pass arguments to run-drawward-cli
%:
		@:
