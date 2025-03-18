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
BACKSTAGE_COMPARE_IMAGE := backstage-compare
BACKSTAGE_COMPARE_BUILD_DIR := docker-files/backstage-compare

DRAWWARD_CLI_IMAGE := drawward-cli
DRAWWARD_CLI_BUILD_DIR := docker-files/drawward-cli

MERMAID_CONVERTER_IMAGE := mermaid-converter
MERMAID_CONVERTER_BUILD_DIR := docker-files/mermaid-converter
MERMAID_BACKSTAGE_CONVERTER_IMAGE := mermaid-to-backstage-converter
MERMAID_BACKSTAGE_CONVERTER_BUILD_DIR := docker-files/mermaid-to-backstage-converter
MERMAID_DIR := docs/design/mermaid
MERMAID_SERVICES := $(notdir $(wildcard $(MERMAID_DIR)/*))

REPO_SLUG ?= myorg/myrepo
TEAM_NAME ?= dev-team
OWNER ?= $(TEAM_NAME)
LIFECYCLE ?= experimental

INPUT_DIR ?= $(DRAWIO_BASE_DIR)
OUTPUT_DIR ?= $(CATALOG_DIR)

SERVICES := $(notdir $(wildcard $(INPUT_DIR)/*))

.PHONY: process-all-common-steps build-drawio-converter-image build-backstage-converter-image build-backstage-lint-image build-drawward-cli-image run-drawward-cli clean process-all-steps-with-drawward-cli backup-all-catalogs validate-all-catalogs convert-mermaid-to-backstage build-mermaid-backstage-converter-image convert-mermaid-to-backstage-% build-backstage-compare-image process-and-compare-mermaid-all $(SERVICES)

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

build-backstage-compare-image:
		@docker build -t $(BACKSTAGE_COMPARE_IMAGE) $(BACKSTAGE_COMPARE_BUILD_DIR) || { echo "Failed to build backstage-compare image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_COMPARE_IMAGE) built successfully"

copy-scripts-to-drawward-cli:
		@cp $(DRAWIO_CONVERTER_BUILD_DIR)/convert_svg_to_xml.sh $(DRAWWARD_CLI_BUILD_DIR)/
		@cp $(BACKSTAGE_CONVERTER_BUILD_DIR)/convert_xml_to_backstage_files.py $(DRAWWARD_CLI_BUILD_DIR)/

build-drawward-cli-image: copy-scripts-to-drawward-cli
		@docker build -t $(DRAWWARD_CLI_IMAGE) $(DRAWWARD_CLI_BUILD_DIR) || { echo "Failed to build drawward-cli image"; exit 1; }
		@echo "Docker image $(DRAWWARD_CLI_IMAGE) built successfully"

build-mermaid-backstage-converter-image:
		@docker build -t $(MERMAID_BACKSTAGE_CONVERTER_IMAGE) $(MERMAID_BACKSTAGE_CONVERTER_BUILD_DIR) || { echo "Failed to build mermaid-backstage-converter image"; exit 1; }
		@echo "Docker image $(MERMAID_BACKSTAGE_CONVERTER_IMAGE) built successfully"

convert-mermaid-to-backstage: $(MERMAID_SERVICES:%=convert-mermaid-to-backstage-%)

convert-mermaid-to-backstage-%: build-mermaid-backstage-converter-image
		@mkdir -p $(OUTPUT_DIR)/$*/systems $(OUTPUT_DIR)/$*/components $(OUTPUT_DIR)/$*/resources $(OUTPUT_DIR)/$*/users $(OUTPUT_DIR)/$*/apis $(OUTPUT_DIR)/$*/domains $(OUTPUT_DIR)/$*/groups
		@echo "Converting Mermaid files to Backstage YAML for service $*"
		@docker run --rm \
				-v "$(PWD)/$(MERMAID_DIR)/$*:/input" \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/output" \
				-e INPUT_DIR="/input" \
				-e OUTPUT_DIR="/output" \
				-e REPO_SLUG=$(REPO_SLUG) \
				-e TEAM_NAME=$(TEAM_NAME) \
				-e OWNER=$(OWNER) \
				-e LIFECYCLE=$(LIFECYCLE) \
				$(MERMAID_BACKSTAGE_CONVERTER_IMAGE) || { echo "Failed to convert Mermaid files to Backstage YAML for $*"; exit 1; }
		@echo "Mermaid files for $* converted to Backstage YAML in $(OUTPUT_DIR)/$*"

# Parameterized target for each service (Draw.io processing only)
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

lint-backstage-files-%: build-backstage-lint-image
		@echo "Linting Backstage files for service $*"
		@docker run --rm \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/app" \
				$(BACKSTAGE_LINT_IMAGE) || { echo "Backstage YAML linting failed for $*"; exit 1; }
		@echo "Backstage YAML files for $* linted successfully"

backup-catalogs-%:
		@mkdir -p $(BACKUP_CATALOG_DIR)/$*/apis $(BACKUP_CATALOG_DIR)/$*/components $(BACKUP_CATALOG_DIR)/$*/resources $(BACKUP_CATALOG_DIR)/$*/systems $(BACKUP_CATALOG_DIR)/$*/users
		@cp -r $(OUTPUT_DIR)/$*/apis/*.yaml $(BACKUP_CATALOG_DIR)/$*/apis/ 2>/dev/null || echo "No API files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/components/*.yaml $(BACKUP_CATALOG_DIR)/$*/components/ 2>/dev/null || echo "No component files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/resources/*.yaml $(BACKUP_CATALOG_DIR)/$*/resources/ 2>/dev/null || echo "No resource files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/systems/*.yaml $(BACKUP_CATALOG_DIR)/$*/systems/ 2>/dev/null || echo "No system files to backup for $*"
		@cp -r $(OUTPUT_DIR)/$*/users/*.yaml $(BACKUP_CATALOG_DIR)/$*/users/ 2>/dev/null || echo "No user files to backup for $*"

validate-catalogs-%: build-backstage-compare-image
		@echo "Validating catalogs for service $*"
		@docker run --rm \
				-v "$(PWD)/$(BACKUP_CATALOG_DIR)/$*:/backup" \
				-v "$(PWD)/$(OUTPUT_DIR)/$*:/generated" \
				-e BACKUP_CATALOG_DIR="/backup" \
				-e BACKSTAGE_CATALOG_DIR="/generated" \
				$(BACKSTAGE_COMPARE_IMAGE) || { echo "Catalog validation failed for $*"; exit 1; }
		@echo "Catalog validation completed successfully for $*"

# New target to process Draw.io, then generate and compare Mermaid files
process-and-compare-mermaid-all: process-all-common-steps convert-mermaid-to-backstage validate-all-catalogs

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

backup-all-catalogs:
		@for service in $(SERVICES); do \
				$(MAKE) backup-catalogs-$$service; \
		done

validate-all-catalogs:
		@for service in $(SERVICES); do \
				$(MAKE) validate-catalogs-$$service; \
		done

process-all-steps-with-drawward-cli: backup-all-catalogs run-drawward-cli validate-all-catalogs

clean:
		@rm -rf $(DRAWIO_XML_DIR) $(OUTPUT_DIR) $(BACKUP_CATALOG_DIR)
		@echo "Cleaned up $(DRAWIO_XML_DIR), $(OUTPUT_DIR)"

%:
		@:
