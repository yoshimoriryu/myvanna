#!/bin/bash

set -e

cleanup() {
  echo "--- Tests finished. Tearing down Docker services... ---"
  docker compose -f docker-compose-tests.yml down
}

trap cleanup EXIT

echo "--- Starting Docker services (Postgres & Qdrant) in the background... ---"
docker compose -f docker-compose-tests.yml up -d

# --- ENHANCEMENT: Wait for services to be healthy ---
echo "--- Waiting for services to become healthy... ---"
max_wait=30
waited=0
# Wait for Postgres
until docker compose -f docker-compose-tests.yml exec -T postgres pg_isready -U postgres &> /dev/null || [ $waited -ge $max_wait ]; do
  echo "Waiting for PostgreSQL... ($waited/$max_wait)"
  sleep 1
  waited=$((waited + 1))
done

if [ $waited -ge $max_wait ]; then
  echo "PostgreSQL did not become healthy in time. Aborting."
  exit 1
fi
echo "PostgreSQL is ready."

echo "--- Running pytest suite... ---"
poetry run pytest -v "$@"