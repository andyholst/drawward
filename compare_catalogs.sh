#!/bin/bash

BACKUP_CATALOG_DIR="${BACKUP_CATALOG_DIR:-backup_catalog}"
BACKSTAGE_CATALOG_DIR="${BACKSTAGE_CATALOG_DIR:-catalog}"

any_comparisons=false

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
                    echo "Comparing $file and $generated_file"
                    if ! diff "$file" "$generated_file" >/dev/null 2>&1; then
                        echo "Error: Differences found in $base_name:"
                        diff "$file" "$generated_file"
                        echo "Validation failed due to differences in $base_name"
                        exit 1
                    else
                        echo "Success: $base_name matches its backup"
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

    # Check if generated directory exists and has files not present in backup
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
