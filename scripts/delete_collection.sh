#!/bin/bash

# This script deletes a specified Qdrant collection.
# It requires the collection name as an argument.

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if a collection name was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <collection_name>"
  echo "Example: ./scripts/delete_collection.sh vanna_students"
  exit 1
fi

COLLECTION_NAME=$1

echo "This will permanently delete the Qdrant collection: '$COLLECTION_NAME'"
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo    # move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]; then
  # We use a small Python script to interact with the Qdrant client
  # because it's easier than crafting a curl command.
  echo "Deleting collection..."
  poetry run python -c "
import config
from qdrant_client import QdrantClient
client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
result = client.delete_collection(collection_name='$COLLECTION_NAME')
if result:
    print(\"Successfully deleted collection: '$COLLECTION_NAME'\")
else:
    print(\"Failed to delete collection or it did not exist.\")
"
fi