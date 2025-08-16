import pytest
from qdrant_client import QdrantClient
import os

from vanna_engine import config
from vanna_engine.my_vanna import MyVanna


@pytest.fixture(scope="module")
def vanna_test_instance():
    """
    Sets up a Vanna instance with a temporary, isolated Qdrant collection
    for the duration of the tests in this module, and cleans it up afterward.
    """
    test_collection_name = f"test_collection_{os.urandom(4).hex()}"
    print(f"\n--- Setting up test instance with collection: {test_collection_name} ---")

    qdrant_client = QdrantClient(url=config.QDRANT_URL)

    # The MyVanna class now requires a full configuration dictionary.
    # We build it here using values from the config module.
    vanna_config = {
        "client": qdrant_client,
        "collection_name": test_collection_name,
        "api_key": config.GEMINI_API_KEY,
        "model": config.VANNA_MODEL,
        "embedding_model": config.VANNA_EMBED_MODEL,
        "temperature": config.VANNA_TEMPERATURE,
        "max_tokens": config.VANNA_MAX_TOKENS,
        "qdrant_url": config.QDRANT_URL
    }

    vn_test = MyVanna(config=vanna_config)
    vn_test.connect_to_postgres(
        host=config.POSTGRES_HOST,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT,
    )

    yield vn_test

    print(f"\n--- Tearing down: Deleting collection '{test_collection_name}' ---")
    try:
        vn_test._client.delete_collection(collection_name=test_collection_name)
        print(f"Successfully deleted collection '{test_collection_name}'.")
    except Exception as e:
        print(f"Error during teardown: Could not delete collection '{test_collection_name}': {e}")


def test_embedding_model_configuration_and_dimensions(vanna_test_instance):
    """
    Verifies the embedding model is configured correctly and produces vectors of the correct size.
    """
    model_name = os.getenv("VANNA_EMBED_MODEL", "models/embedding-001")

    assert model_name.startswith(("models/", "tunedModels/")), (
        f"Invalid model name '{model_name}' found in VANNA_EMBED_MODEL environment variable. "
        "It likely has a typo and should start with 'models/' or 'tunedModels/'."
    )

    KNOWN_DIMENSIONS = {
        "models/embedding-001": 768,
        "text-embedding-004": 3072,
    }

    expected_dimension = KNOWN_DIMENSIONS.get(model_name)
    assert expected_dimension is not None, (
        f"Model '{model_name}' is not in the test suite's list of known models. "
        "Please add its expected dimension to the KNOWN_DIMENSIONS dictionary in the test file."
    )

    print(f"\nVerifying embedding for model '{model_name}'...")
    test_embedding = vanna_test_instance.generate_embedding("This is a test vector")

    print(f"Generated embedding dimension: {len(test_embedding)}. Expected: {expected_dimension}")
    assert (
        len(test_embedding) == expected_dimension
    ), f"Embedding dimension mismatch for model '{model_name}'! Expected {expected_dimension}, got {len(test_embedding)}."
    print("Embedding dimension verification successful.")


def test_full_training_data_lifecycle(vanna_test_instance):
    """Tests the full add, retrieve, and remove lifecycle for all data types."""

    print("\nTesting DDL methods...")
    ddl_id = vanna_test_instance.add_ddl("CREATE TABLE test_table (id INT, name VARCHAR(255))")
    assert ddl_id is not None and ddl_id != "", "Adding DDL failed"
    related_ddl = vanna_test_instance.get_related_ddl("what is in test_table?")
    assert len(related_ddl) > 0, "Getting related DDL failed"

    print("\nTesting Documentation methods...")
    doc_id = vanna_test_instance.add_documentation("The test_table stores test data.")
    assert doc_id is not None and doc_id != "", "Adding documentation failed"
    related_docs = vanna_test_instance.get_related_documentation("what is the test table for?")
    assert len(related_docs) > 0, "Getting related documentation failed"

    print("\nTesting Question/SQL methods...")
    sql_id = vanna_test_instance.add_question_sql(
        question="Show me test data", sql="SELECT * FROM test_table"
    )
    assert sql_id is not None and sql_id != "", "Adding Question/SQL failed"
    similar_sql = vanna_test_instance.get_similar_question_sql("Show me test data")
    assert len(similar_sql) > 0, "Getting similar SQL failed"

    print("\nTesting retrieval of all training data...")
    all_data = vanna_test_instance.get_training_data()
    assert len(all_data) == 3, "Incorrect number of training data points retrieved"
    print(f"Successfully retrieved {len(all_data)} data points.")

    print("\nTesting removal of training data...")
    assert vanna_test_instance.remove_training_data([ddl_id]), "Removing DDL failed"
    assert vanna_test_instance.remove_training_data([doc_id]), "Removing documentation failed"
    assert vanna_test_instance.remove_training_data([sql_id]), "Removing Question/SQL failed"
    print("Successfully removed all training data.")

    print("\nVerifying removal...")
    all_data_after_removal = vanna_test_instance.get_training_data()
    assert len(all_data_after_removal) == 0, "Training data not removed correctly"
    print("Successfully verified that collection is empty after removal.")


def test_get_sql_method(vanna_test_instance):
    """Tests the end-to-end SQL generation via the new get_sql method."""
    print("\nTesting get_sql method...")

    # First, add some context so the model has something to work with.
    ddl_id = vanna_test_instance.add_ddl(
        "CREATE TABLE customers (id INT, name VARCHAR(255), email VARCHAR(255))"
    )
    assert ddl_id, "Failed to add DDL for get_sql test"

    question = "Show me the names of all customers"
    generated_sql = vanna_test_instance.get_sql(question)

    print(f"Question: '{question}'")
    print(f"Generated SQL: {generated_sql}")

    assert generated_sql is not None, "get_sql should not return None"
    assert isinstance(generated_sql, str), "get_sql should return a string"
    assert "customers" in generated_sql.lower(), "Generated SQL should reference the correct table"
    assert "name" in generated_sql.lower(), "Generated SQL should reference the correct column"
