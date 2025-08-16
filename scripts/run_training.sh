#!/bin/bash

# This script provides a convenient way to train a specific Vanna domain.
# It takes the domain name as an argument and constructs the necessary
# file paths and collection name for the training.py script.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Validation ---
if [ -z "$1" ]; then
  echo "Usage: $0 <domain_name>"
  echo "Example: ./scripts/run_training.sh students"
  exit 1
fi

DOMAIN=$1
COLLECTION_NAME="vanna_${DOMAIN}"
BASE_PATH="training_data/${DOMAIN}"

DDL_FILE="${BASE_PATH}/ddl.sql"
DOCS_FILE="${BASE_PATH}/docs.txt"
SQL_FILE="${BASE_PATH}/sql.json"

echo "--- Preparing to train domain: '$DOMAIN' ---"
echo "Target Collection: $COLLECTION_NAME"
echo "DDL File: $DDL_FILE"
echo "Docs File: $DOCS_FILE"
echo "SQL File: $SQL_FILE"
echo "------------------------------------------"

# --- Check if training files exist ---
if [ ! -f "$DDL_FILE" ] || [ ! -f "$DOCS_FILE" ] || [ ! -f "$SQL_FILE" ]; then
  echo "Error: One or more training files are missing for the domain '$DOMAIN'."
  echo "Please ensure the following files exist:"
  echo "- $DDL_FILE"
  echo "- $DOCS_FILE"
  echo "- $SQL_FILE"
  exit 1
fi

# --- Run the Trainer ---
# Execute the generic training script with the arguments built from the domain name.
poetry run python apps/synchronizer.py \
    --collection-name "$COLLECTION_NAME" \
    --ddl-file "$DDL_FILE" \
    --docs-file "$DOCS_FILE" \
    --sql-file "$SQL_FILE"

echo "--- Training for domain '$DOMAIN' complete. ---"
