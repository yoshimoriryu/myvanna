Run
#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Validation ---
if [ -z "$1" ]; then
  echo "Usage: $0 <domain_name>"
  echo "Example: ./scripts/run_training.sh students"
  exit 1
fi

DOMAIN=$1

echo "--- Preparing to train domain: '$DOMAIN' via Docker ---"

# --- Run the Synchronizer Tool Inside a One-Off Docker Container ---
# `docker compose run`: Starts a new container for a service.
# `--rm`: Automatically removes the container after the command exits.
# `app`: The name of the service in docker-compose.yml to use.
# `poetry run python ...`: The command to execute *inside* the container.
docker compose run --rm chatbot-api python tools/synchronizer.py "$DOMAIN"
