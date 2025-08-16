import argparse
import json
import logging
from typing import Dict, Any

from vanna_engine import config
from vanna_engine.my_vanna import MyVanna
from qdrant_client import QdrantClient


def load_local_data(
    vn: MyVanna, ddl_file: str, docs_file: str, sql_file: str
) -> Dict[str, Dict[str, Any]]:
    """
    Loads all training data from local files and maps it by its deterministic ID.

    Returns:
        A dictionary mapping { "deterministic_id": { "type": "...", "content": ... } }
    """
    local_data_map = {}
    print("\n--- Loading and Hashing Local Training Data ---")

    # Load DDL files
    if ddl_file:
        print(f"Loading DDL from {ddl_file}...")
        with open(ddl_file, "r") as f:
            ddl_statements = [stmt.strip() for stmt in f.read().split(";\n") if stmt.strip()]
        for ddl in ddl_statements:
            entry_id = vn.get_deterministic_id(ddl)
            local_data_map[entry_id] = {"type": "ddl", "content": ddl}
        print(f"Found {len(ddl_statements)} local DDL entries.")

    # Load documentation files
    if docs_file:
        print(f"Loading docs from {docs_file}...")
        with open(docs_file, "r") as f:
            docs = [line.strip() for line in f.readlines() if line.strip()]
        for doc in docs:
            entry_id = vn.get_deterministic_id(doc)
            local_data_map[entry_id] = {"type": "documentation", "content": doc}
        print(f"Found {len(docs)} local documentation entries.")

    # Load SQL files
    if sql_file:
        print(f"Loading SQL from {sql_file}...")
        with open(sql_file, "r") as f:
            sql_pairs = json.load(f)
        for pair in sql_pairs:
            if "question" in pair and "sql" in pair:
                # For SQL pairs, the question is the unique content
                entry_id = vn.get_deterministic_id(pair["question"])
                local_data_map[entry_id] = {
                    "type": "sql",
                    "question": pair["question"],
                    "sql": pair["sql"],
                }
        print(f"Found {len(sql_pairs)} local SQL entries.")

    return local_data_map


def main():
    """
    A generic Vanna trainer that synchronizes a Qdrant collection with
    local training data files, performing surgical updates, additions,
    and deletions.
    """
    parser = argparse.ArgumentParser(description="Vanna RAG Synchronizer")
    parser.add_argument(
        "--collection-name", required=True, help="The name of the Qdrant collection to synchronize."
    )
    parser.add_argument("--ddl-file", help="Path to a .sql file with DDL statements.")
    parser.add_argument("--docs-file", help="Path to a .txt file with documentation.")
    parser.add_argument("--sql-file", help="Path to a .json file with SQL question-answer pairs.")
    args = parser.parse_args()

    print(f"--- Vanna Synchronizer Initializing for collection: '{args.collection_name}' ---")

    qdrant_client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    vanna_config = config.VANNA_CONFIG_DICT.copy()
    vanna_config["client"] = qdrant_client
    vanna_config["collection_name"] = args.collection_name
    vn = MyVanna(config=vanna_config)

    # --- Step 1: Load Local State ---
    local_data_map = load_local_data(vn, args.ddl_file, args.docs_file, args.sql_file)
    local_ids = set(local_data_map.keys())

    # --- Step 2: Fetch Remote State ---
    print("\n--- Fetching Remote State from Qdrant ---")
    remote_ids = set(vn.get_all_training_data_ids())
    print(f"Found {len(remote_ids)} existing entries in collection '{args.collection_name}'.")

    # --- Step 3: Calculate the Diff ---
    print("\n--- Calculating Differences ---")
    ids_to_add = local_ids - remote_ids
    ids_to_remove = remote_ids - local_ids

    print(f"Found {len(ids_to_add)} new or modified entries to upsert.")
    print(f"Found {len(ids_to_remove)} outdated entries to remove.")

    # --- Step 4: Execute the Plan ---
    print("\n--- Executing Synchronization Plan ---")

    # Perform Deletions
    if ids_to_remove:
        print(f"Removing {len(ids_to_remove)} entries...")
        vn.remove_training_data(list(ids_to_remove))
    else:
        print("No entries to remove.")

    # Perform Additions/Updates
    if ids_to_add:
        print(f"Upserting {len(ids_to_add)} entries...")
        for entry_id in ids_to_add:
            data = local_data_map[entry_id]
            if data["type"] == "ddl":
                vn.add_ddl(data["content"])
            elif data["type"] == "documentation":
                vn.add_documentation(data["content"])
            elif data["type"] == "sql":
                vn.add_question_sql(question=data["question"], sql=data["sql"])
    else:
        print("No new or modified entries to upsert.")

    print("\n--- Synchronization Complete ---")
    try:
        training_data = vn.get_training_data()
        print(
            f"\nFinal state: {len(training_data)} total entries in collection '{args.collection_name}'."
        )
    except Exception as e:
        logging.error(f"An error occurred while fetching final training data count: {e}")


if __name__ == "__main__":
    main()
