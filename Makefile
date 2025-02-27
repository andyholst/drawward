SHELL := /bin/bash

DOCKER_IMAGE := drawio-converter
DOCKER_BUILD_DIR := docker-files/draw-io
SVG_DIR := docs/design/drawio
XML_DIR := docs/design/xml

.PHONY: all build-drawio-image convert-drawio-svg-to-xml

all: convert-drawio-svg-to-xml

build-drawio-image:
		docker build --no-cache -t $(DOCKER_IMAGE) $(DOCKER_BUILD_DIR) || { echo "Failed to build Docker image"; exit 1; }
		@echo "Docker image $(DOCKER_IMAGE) built successfully"

convert-drawio-svg-to-xml: build-drawio-image
		mkdir -p $(XML_DIR)
		@echo "Running: docker run --rm -v \"$(PWD)/$(SVG_DIR)\":/input -v \"$(PWD)/$(XML_DIR)\":/output $(DOCKER_IMAGE)"
		docker run --rm \
				-v "$(PWD)/$(SVG_DIR)":/input \
				-v "$(PWD)/$(XML_DIR)":/output \
				$(DOCKER_IMAGE) || { echo "Failed to convert SVG files to XML"; exit 1; }
		@echo "SVG files converted to XML in $(XML_DIR)"

