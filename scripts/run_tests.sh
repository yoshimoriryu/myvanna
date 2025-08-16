#!/bin/bash

set -e

# Define the paths to the compose file and the test environment file
COMPOSE_FILE="docker-compose-tests.yml"
ENV_FILE=".env.test"

cleanup() {
  echo "--- Tests finished. Tearing down Docker services... ---"
  # Use the env file for the down command as well
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
}

trap cleanup EXIT

echo "--- Exporting test environment variables from $ENV_FILE ---"
# This command exports the variables from the .env.test file into the script's environment.
# This ensures that pytest and the underlying python code know which ports to connect to.
export $(cat "$ENV_FILE" | xargs)

echo "--- Starting Docker services for tests in the background... ---"
# Use the --env-file flag to tell docker compose which environment to use
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo "--- Waiting for services to initialize... ---"
sleep 5

echo "--- Running pytest suite... ---"
poetry run pytest -v "$@"