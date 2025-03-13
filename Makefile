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

REPO_SLUG ?= myorg/myrepo
TEAM_NAME ?= dev-team
OWNER ?= $(TEAM_NAME)
LIFECYCLE ?= experimental

# List of service directories under DRAWIO_BASE_DIR
SERVICES := $(notdir $(wildcard $(DRAWIO_BASE_DIR)/*))

.PHONY: all build-drawio-converter-image build-backstage-converter-image build-backstage-lint-image clean $(SERVICES)

# Default target: process all services
all: $(SERVICES)

build-drawio-converter-image:
		docker build -t $(DRAWIO_CONVERTER_IMAGE) $(DRAWIO_CONVERTER_BUILD_DIR) || { echo "Failed to build Docker image"; exit 1; }
		@echo "Docker image $(DRAWIO_CONVERTER_IMAGE) built successfully"

build-backstage-converter-image:
		docker build -t $(BACKSTAGE_CONVERTER_IMAGE) $(BACKSTAGE_CONVERTER_BUILD_DIR) || { echo "Failed to build XML-to-YAML Docker image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_CONVERTER_IMAGE) built successfully"

build-backstage-lint-image:
		docker build -t $(BACKSTAGE_LINT_IMAGE) $(BACKSTAGE_LINT_BUILD_DIR) || { echo "Failed to build Backstage lint Docker image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_LINT_IMAGE) built successfully"

# Parameterized target for each service
$(SERVICES): %: backup-catalogs-% convert-drawio-svg-to-xml-% convert-xml-to-backstage-files-% lint-backstage-files-% validate-catalogs-%

convert-drawio-svg-to-xml-%: build-drawio-converter-image
		mkdir -p $(DRAWIO_XML_DIR)/$*
		@echo "Converting SVG to XML for service $*"
		docker run --rm \
				-v "$(PWD)/$(DRAWIO_BASE_DIR)/$*":/input \
				-v "$(PWD)/$(DRAWIO_XML_DIR)/$*":/output \
				$(DRAWIO_CONVERTER_IMAGE) || { echo "Failed to convert SVG files to XML for $*"; exit 1; }
		@echo "SVG files for $* converted to XML in $(DRAWIO_XML_DIR)/$*"

# Convert XML to Backstage files for a specific service
convert-xml-to-backstage-files-%: build-backstage-converter-image
		mkdir -p catalog/$*/systems catalog/$*/components catalog/$*/resources catalog/$*/users catalog/$*/apis
		@echo "Converting XML to Backstage files for service $*"
		docker run --rm \
				-v "$(PWD)/$(DRAWIO_XML_DIR)/$*":/input \
				-v "$(PWD)/catalog/$*":/output \
				-e REPO_SLUG=$(REPO_SLUG) \
				-e TEAM_NAME=$(TEAM_NAME) \
				-e OWNER=$(OWNER) \
				-e LIFECYCLE=$(LIFECYCLE) \
				$(BACKSTAGE_CONVERTER_IMAGE) || { echo "Failed to convert XML files to Backstage YAML for $*"; exit 1; }
		@echo "XML files for $* converted to Backstage YAML in catalog/$*"

# Lint Backstage files for a specific service
lint-backstage-files-%: build-backstage-lint-image
		@echo "Linting Backstage files for service $*"
		docker run --rm \
				-v "$(PWD)/catalog/$*":/app \
				$(BACKSTAGE_LINT_IMAGE) || { echo "Backstage YAML linting failed for $*"; exit 1; }
		@echo "Backstage YAML files for $* linted successfully"

# Backup catalogs for a specific service
backup-catalogs-%:
		mkdir -p $(BACKUP_CATALOG_DIR)/$*/apis $(BACKUP_CATALOG_DIR)/$*/components $(BACKUP_CATALOG_DIR)/$*/resources $(BACKUP_CATALOG_DIR)/$*/systems $(BACKUP_CATALOG_DIR)/$*/users
		cp -r catalog/$*/apis/*.yaml $(BACKUP_CATALOG_DIR)/$*/apis/ 2>/dev/null || echo "No API files to backup for $*"
		cp -r catalog/$*/components/*.yaml $(BACKUP_CATALOG_DIR)/$*/components/ 2>/dev/null || echo "No component files to backup for $*"
		cp -r catalog/$*/resources/*.yaml $(BACKUP_CATALOG_DIR)/$*/resources/ 2>/dev/null || echo "No resource files to backup for $*"
		cp -r catalog/$*/systems/*.yaml $(BACKUP_CATALOG_DIR)/$*/systems/ 2>/dev/null || echo "No system files to backup for $*"
		cp -r catalog/$*/users/*.yaml $(BACKUP_CATALOG_DIR)/$*/users/ 2>/dev/null || echo "No user files to backup for $*"

# Validate catalogs for a specific service
validate-catalogs-%:
		@BACKUP_CATALOG_DIR="$(BACKUP_CATALOG_DIR)/$*" BACKSTAGE_CATALOG_DIR="catalog/$*" bash compare_catalogs.sh || { echo "Catalog validation failed for $*"; exit 1; }
		@echo "Catalog validation completed successfully for $*"

# Clean up generated files
clean:
		rm -rf $(DRAWIO_XML_DIR) catalog
		@echo "Cleaned up $(DRAWIO_XML_DIR) and catalog"
