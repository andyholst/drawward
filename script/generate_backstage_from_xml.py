import xml.etree.ElementTree as ET
import os
import json

# Directory setup
xml_dir = "docs/design/xml"
output_dir = "docs/design/backstage"
os.makedirs(output_dir, exist_ok=True)

# Initialize data structures
entities = {}
relationships = []
current_system = None
current_container = None

# Load and parse all XML files
for xml_file in ["System.xml", "Container.xml", "Component.xml"]:
    xml_path = os.path.join(xml_dir, xml_file)
    if not os.path.exists(xml_path):
        print(f"Warning: {xml_path} not found, skipping...")
        continue

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Parse C4 elements (objects with labels)
    for obj in root.findall(".//object"):
        label = obj.get("label", "")
        if not label:
            continue
        name = label.split("\n")[0]
        desc = obj.get("description", "") or (label[len(name)+1:] if "\n" in label else "")
        entity_id = obj.get("id")
        cell = obj.find(".//mxCell")
        style = cell.get("style", "") if cell else ""

        # Map C4 levels to entity types
        if "person" in style:
            entities[entity_id] = {"type": "person", "name": name, "var": name.lower().replace(" ", "")}
        elif "system" in style:
            entities[entity_id] = {"type": "System", "name": name, "description": desc}
            current_system = entity_id
            current_container = None
        elif "container" in style:
            kind = "Component" if "Service" in name else "Resource"
            entities[entity_id] = {"type": kind, "name": name, "description": desc, "system": current_system}
            current_container = entity_id if kind == "Component" else None
        elif "component" in style and current_container:
            entities[entity_id] = {"type": "component", "name": name, "description": desc, "parent": current_container}

    # Parse relationships (edges)
    for cell in root.findall(".//mxCell[@edge='1']"):
        source = cell.get("source")
        target = cell.get("target")
        label = cell.get("value", "")
        if source in entities and target in entities:
            relationships.append((source, target, label))

# Generate Backstage catalog-info.yaml files
def write_catalog_info(entity, kind, filename, system=None, deps=None):
    catalog = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": kind,
        "metadata": {
            "name": entity["name"].lower().replace(" ", "-"),
            "description": entity["description"]
        },
        "spec": {"owner": "team-a"}
    }
    if kind == "Component":
        catalog["spec"]["type"] = "service"
        catalog["spec"]["lifecycle"] = "experimental"
        if system:
            catalog["spec"]["system"] = entities[system]["name"].lower().replace(" ", "-")
        if deps:
            catalog["spec"]["dependsOn"] = [f"resource:{entities[dep]['name'].lower().replace(' ', '-')}" for dep in deps]
    elif kind == "Resource":
        catalog["spec"]["type"] = "database"
        if system:
            catalog["spec"]["system"] = entities[system]["name"].lower().replace(" ", "-")
    with open(os.path.join(output_dir, filename), "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"Generated {filename}")

# Generate Helm chart for Components
def generate_helm_chart(component_name):
    helm_dir = os.path.join(output_dir, f"{component_name}/helm/templates")
    os.makedirs(helm_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, f"{component_name}/helm/Chart.yaml"), "w") as f:
        f.write(f"""apiVersion: v2
name: {component_name}
description: Helm chart for {component_name}
type: application
version: 0.1.0
appVersion: "0.0.1"
""")
    
    with open(os.path.join(output_dir, f"{component_name}/helm/values.yaml"), "w") as f:
        f.write(f"""replicaCount: 1
image:
  repository: {component_name}
  tag: "latest"
service:
  type: ClusterIP
  port: 80
""")
    
    with open(os.path.join(helm_dir, "deployment.yaml"), "w") as f:
        f.write(f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {component_name}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {component_name}
  template:
    metadata:
      labels:
        app: {component_name}
    spec:
      containers:
      - name: {component_name}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 8080
""")
    
    with open(os.path.join(helm_dir, "service.yaml"), "w") as f:
        f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {component_name}-service
spec:
  selector:
    app: {component_name}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: 8080
  type: {{ .Values.service.type }}
""")
    print(f"Generated Helm chart for {component_name}")

# Generate Spring Boot OAuth2 code with C4 Components as implementation details
def generate_spring_boot_oauth2(component_name, components):
    src_dir = os.path.join(output_dir, f"{component_name}/src/main/java/com/example")
    os.makedirs(src_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, f"{component_name}/pom.xml"), "w") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>{component_name}</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.3</version>
  </parent>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-oauth2-client</artifactId>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
</project>
""")
    
    # Embed C4 Components (OAuth2 Client, API Controller) as methods
    with open(os.path.join(src_dir, "Application.java"), "w") as f:
        f.write(f"""package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class Application {{
    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}

    // OAuth2 Client logic (C4 Component)
    private String getUserInfo(OAuth2AuthenticationToken token) {{
        return "User: " + token.getPrincipal().getName();
    }}

    // API Controller logic (C4 Component)
    @GetMapping("/")
    public String home(OAuth2AuthenticationToken token) {{
        return "Hello, " + getUserInfo(token) + "!";
    }}
}}
""")
    print(f"Generated Spring Boot OAuth2 code for {component_name}")

# Process entities and generate files
for entity_id, entity in entities.items():
    name = entity["name"].lower().replace(" ", "-")
    if entity["type"] == "System":
        write_catalog_info(entity, "System", f"{name}.yaml")
    elif entity["type"] in ["Component", "Resource"]:
        deps = [rel[1] for rel in relationships if rel[0] == entity_id and entities[rel[1]]["type"] == "Resource"]
        write_catalog_info(entity, entity["type"], f"{name}.yaml", entity["system"], deps)
        if entity["type"] == "Component":
            # Find C4 Components within this Container
            components = [e for e in entities.values() if e.get("parent") == entity_id and e["type"] == "component"]
            generate_helm_chart(name)
            generate_spring_boot_oauth2(name, components)

print("Backstage files generated in docs/design/backstage")