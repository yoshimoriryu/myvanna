import argparse
import json
import logging

import config
from my_vanna import MyVanna
from qdrant_client import QdrantClient


def train_from_ddl(vn: MyVanna, file_path: str):
    """Loads DDL statements from a file and trains the Vanna instance."""
    print(f"\nAdding DDL statements from {file_path}...")
    with open(file_path, "r") as f:
        # Assumes DDL statements are separated by a semicolon and a newline
        ddl_statements = [stmt.strip() for stmt in f.read().split(";\n") if stmt.strip()]

    for ddl in ddl_statements:
        vn.add_ddl(ddl)
    print(f"Successfully added {len(ddl_statements)} DDL statements.")


def train_from_docs(vn: MyVanna, file_path: str):
    """Loads documentation from a file and trains the Vanna instance."""
    print(f"\nAdding documentation from {file_path}...")
    with open(file_path, "r") as f:
        # Assumes each line in the file is a separate piece of documentation
        docs = [line.strip() for line in f.readlines() if line.strip()]

    for doc in docs:
        vn.add_documentation(doc)
    print(f"Successfully added {len(docs)} documentation entries.")


def train_from_sql(vn: MyVanna, file_path: str):
    """Loads SQL question-answer pairs from a JSON file and trains the Vanna instance."""
    print(f"\nAdding SQL training pairs from {file_path}...")
    with open(file_path, "r") as f:
        sql_pairs = json.load(f)

    for pair in sql_pairs:
        if "question" in pair and "sql" in pair:
            vn.add_question_sql(question=pair["question"], sql=pair["sql"])
    print(f"Successfully added {len(sql_pairs)} SQL training pairs.")


def main():
    """
    A generic Vanna trainer that populates a specified Qdrant collection
    with training data provided from files.
    """
    parser = argparse.ArgumentParser(description="Generic Vanna Trainer")
    parser.add_argument(
        "--collection-name", required=True, help="The name of the Qdrant collection to train."
    )
    parser.add_argument("--ddl-file", help="Path to a .sql file with DDL statements.")
    parser.add_argument("--docs-file", help="Path to a .txt file with documentation.")
    parser.add_argument("--sql-file", help="Path to a .json file with SQL question-answer pairs.")
    args = parser.parse_args()

    print(f"--- Vanna Training Initializing for collection: '{args.collection_name}' ---")

    qdrant_client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)

    # Use the master config, but override the collection name with the CLI argument
    vanna_config = config.VANNA_CONFIG_DICT.copy()
    vanna_config["client"] = qdrant_client
    vanna_config["collection_name"] = args.collection_name

    vn = MyVanna(config=vanna_config)

    print("\n--- Starting Training Data Population ---")
    if args.ddl_file:
        train_from_ddl(vn, args.ddl_file)
    if args.docs_file:
        train_from_docs(vn, args.docs_file)
    if args.sql_file:
        train_from_sql(vn, args.sql_file)

    print("\n--- Training Complete ---")

    try:
        training_data = vn.get_training_data()
        print("\n--- Current Training Data Summary ---")
        if not training_data.empty:
            print(f"Total entries in collection '{args.collection_name}': {len(training_data)}")
            print(training_data.head())
        else:
            print(f"No training data found in collection '{args.collection_name}'.")
        print("-----------------------------------\n")
    except Exception as e:
        logging.error(f"An error occurred while fetching training data: {e}")


if __name__ == "__main__":
    main()
