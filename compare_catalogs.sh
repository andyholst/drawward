#!/bin/bash

BACKUP_CATALOG_DIR="backup_catalog"
BACKSTAGE_CATALOG_DIR="catalog"

for dir in apis components resources systems users; do
    if [ -d "$BACKUP_CATALOG_DIR/$dir" ]; then
        for file in "$BACKUP_CATALOG_DIR/$dir"/*.yaml; do
            if [ -e "$file" ]; then  # Check if files exist to avoid errors when no files match
                base_name=$(basename "$file")
                generated_file="$BACKSTAGE_CATALOG_DIR/$dir/$base_name"
                if [ -f "$generated_file" ]; then
                    echo "Comparing $file and $generated_file"
                    if ! diff "$file" "$generated_file" > /dev/null 2>&1; then
                        echo "Error: Differences found in $base_name:"
                        diff "$file" "$generated_file"
                        echo "Validation failed due to differences in $base_name"
                        exit 1
                    else
                        echo "Success: $base_name matches its backup"
                    fi
                else
                    echo "Error: Generated file $generated_file not found"
                    exit 1
                fi
            else
                echo "No backup files for $dir, skipping comparison"
                break
            fi
        done
    else
        echo "No backup directory for $dir, skipping comparison"
    fi
done

echo "All generated files match the backup"
