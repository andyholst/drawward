#!/bin/bash

# Default directories if not set via environment variables
BACKUP_CATALOG_DIR="${BACKUP_CATALOG_DIR:-backup_catalog}"
BACKSTAGE_CATALOG_DIR="${BACKSTAGE_CATALOG_DIR:-catalog}"

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "Error: yq is not installed. Please install yq (https://github.com/mikefarah/yq) to proceed."
    exit 1
fi

any_comparisons=false

# Iterate over entity type directories
for dir in apis components resources systems users; do
    backup_dir="$BACKUP_CATALOG_DIR/$dir"
    generated_dir="$BACKSTAGE_CATALOG_DIR/$dir"

    if [ -d "$backup_dir" ]; then
        # Check if there are any backup files
        if ls "$backup_dir"/*.yaml >/dev/null 2>&1; then
            for file in "$backup_dir"/*.yaml; do
                base_name=$(basename "$file")
                generated_file="$generated_dir/$base_name"

                if [ -f "$generated_file" ]; then
                    echo "Comparing $file and $generated_file with sorted lists"
                    # Define the sorting command for relevant lists
                    sort_command='.spec.consumesApis |= sort | .spec.providesApis |= sort | .spec.dependsOn |= sort | .metadata.tags |= sort'
                    # Compare sorted versions of the files in memory, suppressing yq errors
                    if ! diff <(yq eval "$sort_command" "$file" 2>/dev/null) <(yq eval "$sort_command" "$generated_file" 2>/dev/null) >/dev/null 2>&1; then
                        echo "Error: Differences found in $base_name after sorting lists:"
                        # Show the differences between sorted versions (errors still suppressed)
                        diff <(yq eval "$sort_command" "$file" 2>/dev/null) <(yq eval "$sort_command" "$generated_file" 2>/dev/null)
                        echo "Validation failed due to differences in $base_name"
                        exit 1
                    else
                        echo "Success: $base_name matches its backup after sorting lists"
                        any_comparisons=true
                    fi
                else
                    echo "Error: Generated file $generated_file not found for backup $file"
                    exit 1
                fi
            done
        else
            echo "No backup files in $backup_dir, skipping comparison"
        fi
    else
        echo "No backup directory $backup_dir, skipping comparison"
    fi

    # Check for generated files without corresponding backups
    if [ -d "$generated_dir" ] && ls "$generated_dir"/*.yaml >/dev/null 2>&1; then
        for gen_file in "$generated_dir"/*.yaml; do
            gen_base_name=$(basename "$gen_file")
            backup_file="$backup_dir/$gen_base_name"
            if [ ! -f "$backup_file" ] && [ -d "$backup_dir" ]; then
                echo "Error: Generated file $gen_file exists but has no corresponding backup"
                exit 1
            fi
        done
    fi
done

if [ "$any_comparisons" = true ]; then
    echo "All generated files match the backup"
else
    echo "No comparisons made (no backup files found)"
fi
