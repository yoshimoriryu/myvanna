import logging
import os
from typing import Dict, Optional

from qdrant_client import QdrantClient

from vanna_engine import config
from vanna_engine.my_vanna import MyVanna

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
logging.basicConfig(
    level=log_levels.get(config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def initialize_vanna_instances() -> Dict[str, MyVanna]:
    """
    Connects to Qdrant to discover all existing Vanna collections and initializes
    a MyVanna instance for each one.

    This is the "Vanna Factory" - it treats Qdrant as the source of truth for
    what domains are available.

    Returns:
        A dictionary mapping domain names to their configured MyVanna instances.
    """
    logging.info("--- Discovering trained Vanna domains from Qdrant ---")
    instances = {}

    try:
        # Create one client to rule them all
        qdrant_client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)

        # Get all collections that exist in the Qdrant instance
        collections_response = qdrant_client.get_collections()
        all_collections = collections_response.collections

        # Filter for collections that follow our naming convention: 'vanna_<domain_name>'
        vanna_collections = [c for c in all_collections if c.name.startswith("vanna_")]

        for collection in vanna_collections:
            collection_name = collection.name
            # Extract the domain name from the collection name (e.g., 'vanna_students' -> 'students')
            domain = collection_name.replace("vanna_", "", 1)

            logging.info(
                f"Initializing instance for domain: '{domain}' (collection: '{collection_name}')..."
            )

            # Create a specific config for this domain's instance
            vanna_config = config.VANNA_CONFIG_DICT.copy()
            # ADD YOUR CUSTOM PROMPT HERE
            # vanna_config["initial_prompt"] = (
            #     "You are a PostgreSQL expert specializing in university student data. "
            #     "Always refer to tables using their full schema name (e.g., `vanna.v_mahasiswa`). "
            #     "Your response must be a single, executable SQL query and nothing else."
            # )
            # IMPORTANT: We pass the *same* client to all instances for efficiency
            vanna_config["client"] = qdrant_client
            vanna_config["collection_name"] = collection_name

            vn_instance = MyVanna(config=vanna_config)
            vn_instance.connect_to_postgres(
                host=config.POSTGRES_HOST,
                dbname=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                port=config.POSTGRES_PORT,
            )
            instances[domain] = vn_instance

    except Exception as e:
        logging.error(f"\nFATAL ERROR: Could not connect to Qdrant to discover domains: {e}")
        logging.error("Please ensure Qdrant is running and accessible.")
        # Return empty dict so the program can exit gracefully
        return {}

    return instances


def select_domain(domains: list) -> Optional[str]:
    """
    Displays a numbered menu for the user to select a domain.

    Args:
        domains: A list of available domain names.

    Returns:
        The selected domain name as a string, or None if the user wants to exit.
    """

    print("\nPlease select a domain to query:")
    for i, domain in enumerate(domains):
        print(f"  {i + 1}: {domain}")
    print("  0: Exit")

    while True:
        try:
            choice = input("Enter your choice (number): ")
            choice_num = int(choice)
            if choice_num == 0:
                return None
            if 1 <= choice_num <= len(domains):
                return domains[choice_num - 1]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    vanna_instances = initialize_vanna_instances()

    if not vanna_instances:
        print("\nNo domains found in 'training_data' directory. Please run the trainer first.")
        exit()

    domains_list = list(vanna_instances.keys())
    print(f"\n--- Vanna CLI Ready ---")

    while True:
        current_domain = select_domain(domains_list)
        if current_domain is None:
            break

        print(
            f"\nSwitched to domain: '{current_domain}'. You can type 'switch' at any time to change domains."
        )

        while True:
            question = input(f"Ask Vanna (domain: {current_domain}): ")

            if question.lower() == "exit":
                # Allow exiting from the inner loop as well
                current_domain = "exit"
                break
            if question.lower() == "switch":
                break

            try:
                # Get the correct Vanna instance from our dictionary
                active_vanna = vanna_instances[current_domain]

                # Use the get_sql method now built into the class
                generated_sql = active_vanna.get_sql(question)

                if generated_sql:
                    print("\n--- Generated SQL (not executed) ---")
                    print(generated_sql)
                    print("------------------------------------")
                else:
                    print("\nCould not generate SQL for the question.")

            except Exception as e:
                print(f"\nAn error occurred: {e}")

        if current_domain == "exit":
            break

    print("\nGoodbye!")
