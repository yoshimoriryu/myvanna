import os
import sys
import json
import argparse
from typing import List, Dict, Any

# Add project root to the path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
            training_data["ddl"] = [ddl.strip() for ddl in f.read().split(';') if ddl.strip()]
            print(f"Found {len(training_data['ddl'])} DDL statements.")
    except FileNotFoundError:
        print("Warning: 'ddl.sql' not found.")

    try:
        with open(f"{base_path}/docs.txt", "r") as f:
            training_data["documentation"] = [doc.strip() for doc in f.readlines() if doc.strip()]
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
    print(f"Found {len(remote_ids)} existing entries.")

    print("\nStep 3: Upserting local data to Vanna...")
    expected_ids = set()
    for ddl in local_data.get("ddl", []):
        entry_id = vn.add_ddl(ddl)
        if entry_id: expected_ids.add(entry_id)
    for doc in local_data.get("documentation", []):
        entry_id = vn.add_documentation(doc)
        if entry_id: expected_ids.add(entry_id)
    for sql_pair in local_data.get("sql", []):
        entry_id = vn.add_question_sql(sql=sql_pair["sql"], question=sql_pair["question"])
        if entry_id: expected_ids.add(entry_id)
    
    print("\nStep 4: Calculating stale data to be removed...")
    stale_ids = list(remote_ids - expected_ids)
    if stale_ids:
        print(f"Found {len(stale_ids)} stale entries to remove.")
        vn.remove_training_data(ids=stale_ids)
    else:
        print("No stale data found.")

    print(f"\n--- Synchronization for domain '{domain_name}' complete! ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize training data with Vanna.")
    parser.add_argument("domain", help="The domain to synchronize (e.g., 'students').")
    args = parser.parse_args()
    synchronize_domain(args.domain)