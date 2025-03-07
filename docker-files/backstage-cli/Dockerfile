FROM node:22-alpine

RUN npm install -g @roadiehq/backstage-entity-validator

WORKDIR /app

CMD ["sh", "-c", "FAILED=0; for file in $(find /app -name 'catalog-info.yaml'); do echo \"Validating $file\"; output=$(validate-entity \"$file\" 2>&1); if echo \"$output\" | grep -q 'Failed to validate'; then FAILED=1; echo \"$output\"; else echo \"Validation passed for $file\"; fi; done; if [ $FAILED -eq 1 ]; then echo 'One or more validations failed'; exit 1; else echo 'All validations passed'; exit 0; fi"]
