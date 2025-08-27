#!/bin/bash
set -e

# --- CONFIG ---
CONTAINER_NAME="myvanna-private-data-db"
DB_USER="postgres"
DB_NAME="chatbot"

# --- ARGS ---
if [ -z "$1" ]; then
  echo "❌ Usage: $0 path/to/file.sql"
  exit 1
fi

SQL_FILE="$1"

if [ ! -f "$SQL_FILE" ]; then
  echo "❌ SQL file not found: $SQL_FILE"
  exit 1
fi

# --- EXECUTE ---
echo "Injecting $SQL_FILE into $DB_NAME on container $CONTAINER_NAME..."

cat "$SQL_FILE" | docker exec -i "$CONTAINER_NAME" \
  psql -U "$DB_USER" -d "$DB_NAME"

echo "✅ Schema created!"
