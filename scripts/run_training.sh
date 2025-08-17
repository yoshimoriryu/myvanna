#!/bin/bash

# This script provides a convenient way to train a specific Vanna domain.
# It takes the domain name as an argument and passes it to the main
# synchronizer tool.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Validation ---
if [ -z "$1" ]; then
  echo "Usage: $0 <domain_name>"
  echo "Example: ./scripts/run_training.sh students"
  exit 1
fi

DOMAIN=$1
BASE_PATH="training_data/${DOMAIN}"

echo "--- Preparing to train domain: '$DOMAIN' ---"
echo "Looking for training data in: $BASE_PATH"
echo "------------------------------------------"

# --- Check if training directory exists ---
if [ ! -d "$BASE_PATH" ]; then
  echo "Error: Training data directory not found for domain '$DOMAIN'."
  echo "Please ensure the directory '$BASE_PATH' exists."
  exit 1
fi

# --- Run the Synchronizer Tool ---
# The synchronizer script now handles all the logic internally.
poetry run python tools/synchronizer.py "$DOMAIN"

echo "--- Training for domain '$DOMAIN' complete. ---"