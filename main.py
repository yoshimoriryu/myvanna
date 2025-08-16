import logging
from typing import Optional

from qdrant_client import QdrantClient

import config
from my_vanna import MyVanna

# Configure logging
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


if __name__ == "__main__":
    print("--- Vanna CLI Initializing ---")

    # 1. Instantiate the Qdrant client using settings from config.py
    qdrant_client = QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY
    )

    # 2. Instantiate our custom Vanna class, injecting the client
    vn = MyVanna(config={"client": qdrant_client})

    # 3. Connect to the database using settings from config.py
    vn.connect_to_postgres(
        host=config.POSTGRES_HOST,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT,
    )

    print("\n--- Initial Checks ---")
    try:
        training_data = vn.get_training_data()
        print(f"Training data available: {len(training_data) if not training_data.empty else 0} entries")
    except Exception as e:
        print(f"Failed to get training data: {e}")

    try:
        test_result = vn.run_sql("SELECT 1 as test")
        print(f"Database connection test: {'Success' if test_result is not None else 'Failed'}")
    except Exception as e:
        print(f"Database connection error: {e}")

    print("\n--- Vanna CLI Ready (type 'exit' to quit) ---")
    while True:
        question = input("\nAsk Vanna: ")
        if question.lower() == "exit":
            break

        try:
            generated_sql = vn.get_sql(question)
            
            if generated_sql:
                print("\n--- Generated SQL (not executed) ---")
                print(generated_sql)
                print("------------------------------------")
            else:
                print("\nCould not generate SQL for the question.")

        except Exception as e:
            print(f"\nAn error occurred: {e}")

    print("\nGoodbye!")