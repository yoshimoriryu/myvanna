import os
import sys
import json
import argparse
from typing import List, Dict, Any

# Add project root to the path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vanna_engine import config
from src.vanna_engine.my_vanna import MyVanna


def get_training_data_from_folder(domain_name: str) -> Dict[str, List[Any]]:
    """Loads all training data (DDL, Docs, SQL) from a specific domain folder."""
    base_path = f"training_data/{domain_name}"
    if not os.path.isdir(base_path):
        print(f"Error: Training data directory not found at '{base_path}'")
        sys.exit(1)

    training_data = {"ddl": [], "documentation": [], "sql": []}

    try:
        with open(f"{base_path}/ddl.sql", "r") as f:
            training_data["ddl"] = [ddl.strip() for ddl in f.read().split(";") if ddl.strip()]
            print(f"Found {len(training_data['ddl'])} DDL statements.")
    except FileNotFoundError:
        print("Warning: 'ddl.sql' not found.")

    try:
        with open(f"{base_path}/docs.txt", "r") as f:
            training_data["documentation"] = [f.read()]
            print(f"Found {len(training_data['documentation'])} documentation entries.")
    except FileNotFoundError:
        print("Warning: 'docs.txt' not found.")

    try:
        with open(f"{base_path}/sql.json", "r") as f:
            training_data["sql"] = json.load(f)
            print(f"Found {len(training_data['sql'])} SQL question examples.")
    except FileNotFoundError:
        print("Warning: 'sql.json' not found.")

    return training_data


def synchronize_domain(domain_name: str):
    """Synchronizes the training data for a single domain with the Qdrant vector store."""
    print(f"\n--- Starting synchronization for domain: '{domain_name}' ---")

    vanna_config = config.VANNA_CONFIG_DICT.copy()
    vanna_config["collection_name"] = f"vanna_{domain_name}"
    vn = MyVanna(config=vanna_config)

    print("\nStep 1: Loading local training data...")
    local_data = get_training_data_from_folder(domain_name)

    print("\nStep 2: Fetching existing training data IDs from Vanna...")
    remote_ids = set(vn.get_all_training_data_ids())
    print(f"Found {len(remote_ids)} existing entries in collection.")

    # --- NEW: Pre-calculate expected IDs to provide a clear summary ---
    expected_ids = set()
    for ddl in local_data.get("ddl", []):
        expected_ids.add(vn.get_deterministic_id(ddl))
    for doc in local_data.get("documentation", []):
        expected_ids.add(vn.get_deterministic_id(doc))
    for sql_pair in local_data.get("sql", []):
        expected_ids.add(vn.get_deterministic_id(sql_pair["question"]))

    # --- NEW: Calculate and print a detailed summary before taking action ---
    stale_ids = remote_ids - expected_ids
    new_ids = expected_ids - remote_ids
    updated_ids = expected_ids.intersection(remote_ids)

    print("\nStep 3: Synchronization Plan")
    print("---------------------------------")
    print(f"- Total local items found:      {len(expected_ids)}")
    print(f"- New items to be added:        {len(new_ids)}")
    print(f"- Existing items to be updated: {len(updated_ids)}")
    print(f"- Stale remote items to remove: {len(stale_ids)}")
    print("---------------------------------")

    # --- Step 4: Execute the upsert process ---
    print("\nStep 4: Upserting local data to Vanna...")
    items_upserted = 0
    for ddl in local_data.get("ddl", []):
        if vn.add_ddl(ddl):
            items_upserted += 1
    for doc in local_data.get("documentation", []):
        if vn.add_documentation(doc):
            items_upserted += 1
    for sql_pair in local_data.get("sql", []):
        if vn.add_question_sql(sql=sql_pair["sql"], question=sql_pair["question"]):
            items_upserted += 1
    print(f"Successfully upserted {items_upserted} items.")

    # --- Step 5: Execute the removal of stale data ---
    print("\nStep 5: Removing stale data...")
    if stale_ids:
        print(f"Removing {len(stale_ids)} stale entries...")
        vn.remove_training_data(ids=list(stale_ids))
    else:
        print("No stale data to remove.")

    print(f"\n--- Synchronization for domain '{domain_name}' complete! ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize training data with Vanna.")
    parser.add_argument("domain", help="The domain to synchronize (e.g., 'students').")
    args = parser.parse_args()
    synchronize_domain(args.domain)
