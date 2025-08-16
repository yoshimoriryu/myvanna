#!/bin/bash

# This command ensures that the script will exit immediately if any command fails.
set -e

# This function defines the cleanup process.
cleanup() {
  echo "--- Tests finished. Tearing down Docker services... ---"
  # The 'down' command stops and removes the containers.
  docker compose -f docker-compose-tests.yml down
}

# 'trap' is a shell command that registers the 'cleanup' function to be called
# automatically when the script exits, for any reason (success, failure, or interrupt).
# This GUARANTEES that your services will be shut down.
trap cleanup EXIT

echo "--- Starting Docker services (Postgres & Qdrant) in the background... ---"
docker compose -f docker-compose-tests.yml up -d

echo "--- Waiting for services to initialize... ---"
# Give the containers a few seconds to start up and be ready for connections.
sleep 5

echo "--- Running pytest suite... ---"
# Run pytest. The "$@" passes along any arguments you might give to this script.
# For example, running './scripts/run_tests.sh -k "lifecycle"' would work.
poetry run pytest -s "$@"
