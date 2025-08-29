#!/bin/bash

set -e

COMPOSE_FILE="docker-compose-tests.yml"
ENV_FILE=".env.test"
PROJECT_NAME="myvanna-tests"

cleanup() {
  echo "--- Tests finished. Tearing down test Docker environment... ---"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --project-name "$PROJECT_NAME" down
}

trap cleanup EXIT

echo "--- Exporting test environment variables from $ENV_FILE ---"
export $(cat "$ENV_FILE" | xargs)

echo "--- Starting Docker services for tests under project name '$PROJECT_NAME'... ---"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --project-name "$PROJECT_NAME" up -d

echo "--- Waiting for services to initialize... ---"
sleep 5

echo "--- Running pytest suite... ---"
poetry run pytest -v "$@"