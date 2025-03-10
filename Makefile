SHELL := /bin/bash
DRAWIO_CONVERTER_IMAGE := drawio-converter
DRAWIO_CONVERTER_BUILD_DIR := docker-files/drawio-converter
DRAWIO_SVG_DIR := docs/design/drawio
DRAWIO_XML_DIR := docs/design/xml
BACKSTAGE_CONVERTER_IMAGE := backstage-converter
BACKSTAGE_CONVERTER_BUILD_DIR := docker-files/backstage-converter
BACKSTAGE_CATALOG_DIR := catalog
BACKSTAGE_LINT_IMAGE := backstage-lint
BACKSTAGE_LINT_BUILD_DIR := docker-files/backstage-entity-validator
BACKUP_CATALOG_DIR := backup_catalog

REPO_SLUG ?= myorg/myrepo
TEAM_NAME ?= dev-team
OWNER ?= $(TEAM_NAME)
LIFECYCLE ?= experimental

.PHONY: all build-drawio-converter-image convert-drawio-svg-to-xml build-backstage-converter-image convert-xml-to-backstage-files build-backstage-lint-image lint-backstage-files clean backup-catalogs validate-catalogs

all: convert-drawio-svg-to-xml convert-xml-to-backstage-files lint-backstage-files

backup-catalogs:
		mkdir -p $(BACKUP_CATALOG_DIR)/apis $(BACKUP_CATALOG_DIR)/components $(BACKUP_CATALOG_DIR)/resources $(BACKUP_CATALOG_DIR)/systems $(BACKUP_CATALOG_DIR)/users
		cp -r $(BACKSTAGE_CATALOG_DIR)/apis/*.yaml $(BACKUP_CATALOG_DIR)/apis/ 2>/dev/null || echo "No API files to backup"
		cp -r $(BACKSTAGE_CATALOG_DIR)/components/*.yaml $(BACKUP_CATALOG_DIR)/components/ 2>/dev/null || echo "No component files to backup"
		cp -r $(BACKSTAGE_CATALOG_DIR)/resources/*.yaml $(BACKUP_CATALOG_DIR)/resources/ 2>/dev/null || echo "No resource files to backup"
		cp -r $(BACKSTAGE_CATALOG_DIR)/systems/*.yaml $(BACKUP_CATALOG_DIR)/systems/ 2>/dev/null || echo "No system files to backup"
		cp -r $(BACKSTAGE_CATALOG_DIR)/users/*.yaml $(BACKUP_CATALOG_DIR)/users/ 2>/dev/null || echo "No user files to backup"

validate-catalogs:
		@bash compare_catalogs.sh
		@echo "Catalog validation completed successfully"

build-drawio-converter-image:
		docker build -t $(DRAWIO_CONVERTER_IMAGE) $(DRAWIO_CONVERTER_BUILD_DIR) || { echo "Failed to build Docker image"; exit 1; }
		@echo "Docker image $(DRAWIO_CONVERTER_IMAGE) built successfully"

convert-drawio-svg-to-xml: build-drawio-converter-image
		mkdir -p $(DRAWIO_XML_DIR)
		@echo "Running: docker run --rm -v \"$(PWD)/$(DRAWIO_SVG_DIR)\":/input -v \"$(PWD)/$(DRAWIO_XML_DIR)\":/output $(DRAWIO_CONVERTER_IMAGE)"
		docker run --rm \
				-v "$(PWD)/$(DRAWIO_SVG_DIR)":/input \
				-v "$(PWD)/$(DRAWIO_XML_DIR)":/output \
				$(DRAWIO_CONVERTER_IMAGE) || { echo "Failed to convert SVG files to XML"; exit 1; }
		@echo "SVG files converted to XML in $(DRAWIO_XML_DIR)"

build-backstage-converter-image:
		docker build -t $(BACKSTAGE_CONVERTER_IMAGE) $(BACKSTAGE_CONVERTER_BUILD_DIR) || { echo "Failed to build XML-to-YAML Docker image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_CONVERTER_IMAGE) built successfully"

convert-xml-to-backstage-files: build-backstage-converter-image
		mkdir -p $(BACKSTAGE_CATALOG_DIR)/systems $(BACKSTAGE_CATALOG_DIR)/components $(BACKSTAGE_CATALOG_DIR)/resources $(BACKSTAGE_CATALOG_DIR)/users
		@echo "Running: docker run --rm -v \"$(PWD)/$(DRAWIO_XML_DIR)\":/input -v \"$(PWD)/$(BACKSTAGE_CATALOG_DIR)\":/output -e REPO_SLUG=$(REPO_SLUG) -e TEAM_NAME=$(TEAM_NAME) -e OWNER=$(OWNER) -e LIFECYCLE=$(LIFECYCLE) $(BACKSTAGE_CONVERTER_IMAGE)"
		docker run --rm \
				-v "$(PWD)/$(DRAWIO_XML_DIR)":/input \
				-v "$(PWD)/$(BACKSTAGE_CATALOG_DIR)":/output \
				-e REPO_SLUG=$(REPO_SLUG) \
				-e TEAM_NAME=$(TEAM_NAME) \
				-e OWNER=$(OWNER) \
				-e LIFECYCLE=$(LIFECYCLE) \
				$(BACKSTAGE_CONVERTER_IMAGE) || { echo "Failed to convert XML files to Backstage YAML"; exit 1; }
		@echo "XML files converted to Backstage YAML in $(BACKSTAGE_CATALOG_DIR)"

build-backstage-lint-image:
		docker build -t $(BACKSTAGE_LINT_IMAGE) $(BACKSTAGE_LINT_BUILD_DIR) || { echo "Failed to build Backstage lint Docker image"; exit 1; }
		@echo "Docker image $(BACKSTAGE_LINT_IMAGE) built successfully"

lint-backstage-files: build-backstage-lint-image
		@echo "Running: docker run --rm -v \"$(PWD)/$(BACKSTAGE_CATALOG_DIR)\":/app $(BACKSTAGE_LINT_IMAGE)"
		docker run --rm \
				-v "$(PWD)/$(BACKSTAGE_CATALOG_DIR)":/app \
				$(BACKSTAGE_LINT_IMAGE) || { echo "Backstage YAML linting failed"; exit 1; }
		@echo "Backstage YAML files linted successfully"

clean:
		rm -rf $(DRAWIO_XML_DIR) $(BACKSTAGE_CATALOG_DIR)
		@echo "Cleaned up $(DRAWIO_XML_DIR) and $(BACKSTAGE_CATALOG_DIR)"
