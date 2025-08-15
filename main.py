import logging
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from vanna.google import GoogleGeminiChat
import os
from dotenv import load_dotenv
from vanna.base import VannaBase
import google.generativeai as genai
from typing import List, Optional, Dict, Any
from abc import abstractmethod
import pandas as pd


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VANNA_MODEL = os.getenv("VANNA_MODEL", "gemini-1.5-pro")
VANNA_EMBED_MODEL = os.getenv("VANNA_EMBED_MODEL", "gemini-embedding-001")
VANNA_TEMPERATURE = os.getenv("VANNA_TEMPERATURE", 0.1)
VANNA_COLLECTION_NAME = os.getenv("VANNA_COLLECTION_NAME", "myvanna_sql_collection")
VANNA_MAX_TOKENS = os.getenv("VANNA_MAX_TOKENS", 2048)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logging.basicConfig(
    level=log_levels.get(LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class MyVanna(Qdrant_VectorStore, GoogleGeminiChat):
    """
    Custom Vanna implementation using Google Gemini and Qdrant
    """

    def __init__(self, config: Optional[Dict] = None):
        genai.configure(api_key=GEMINI_API_KEY)

        VannaBase.__init__(self, config=config)

        self.model_name = VANNA_MODEL
        self.embedding_model = VANNA_EMBED_MODEL
        self.collection_name = config.get("collection_name", VANNA_COLLECTION_NAME)
        self.max_tokens = VANNA_MAX_TOKENS

        qdrant_store_config = {
            "client": QdrantClient(url=QDRANT_URL),
            "collection_name": self.collection_name,
            "documentation_collection_name": self.collection_name,
            "ddl_collection_name": self.collection_name,
            "sql_collection_name": self.collection_name,
        }

        gemini_config = {
            "api_key": GEMINI_API_KEY,
            "model_name": self.model_name,
            "temperature": VANNA_TEMPERATURE,
            "embed_model": self.embedding_model,
        }

        Qdrant_VectorStore.__init__(self, config=qdrant_store_config)
        GoogleGeminiChat.__init__(self, config=gemini_config)

        print(f"chat model: {self.chat_model}")
        print(f"embedding model: {self.embedding_model}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using Google's Gemini embedding model.
        Args:
            text: The text to generate embeddings for
        Returns:
            A list of floats representing the embedding vector
        """
        try:
            if not text or not isinstance(text, str):
                print(f"Warning: Invalid data for embedding: {text}")
                return []

            result = genai.embed_content(
                model=self.embedding_model, content=text, task_type="retrieval_document"
            )

            return result["embedding"]

        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        """
        This method is used to get similar questions and their corresponding SQL statements.

        Args:
            question (str): The question to get similar questions and their corresponding SQL statements for.

        Returns:
            list: A list of similar questions and their corresponding SQL statements.
        """
        try:

            question_embedding = self.generate_embedding(question)

            results = self._client.query_points(
                collection_name=self.sql_collection_name,
                query=question_embedding,
                limit=kwargs.get("limit", 5),
                with_payload=True,
            )

            similar_questions = []
            for result in results.points:
                if result.payload and "question" in result.payload and "sql" in result.payload:
                    similar_questions.append(
                        {
                            "question": result.payload["question"],
                            "sql": result.payload["sql"],
                            "similarity": result.score,
                        }
                    )

            return similar_questions
        except Exception as e:
            logging.error(f"Error getting similar questions: {e}")
            return []

    def get_related_ddl(self, question: str, **kwargs) -> list:
        """
        This method is used to get related DDL statements to a question.

        Args:
            question (str): The question to get related DDL statements for.

        Returns:
            list: A list of related DDL statements.
        """
        try:

            question_embedding = self.generate_embedding(question)

            results = self._client.query_points(
                collection_name=self.ddl_collection_name,
                query=question_embedding,
                limit=kwargs.get("limit", 5),
                with_payload=True,
            )

            related_ddl = []
            for result in results.points:
                if result.payload and "ddl" in result.payload:
                    related_ddl.append({"ddl": result.payload["ddl"], "similarity": result.score})

            return related_ddl
        except Exception as e:
            logging.error(f"Error getting related DDL: {e}")
            return []

    def get_related_documentation(self, question: str, **kwargs) -> list:
        """
        This method is used to get related documentation to a question.

        Args:
            question (str): The question to get related documentation for.

        Returns:
            list: A list of related documentation.
        """
        try:

            question_embedding = self.generate_embedding(question)

            results = self._client.query_points(
                collection_name=self.documentation_collection_name,
                query=question_embedding,
                limit=kwargs.get("limit", 5),
                with_payload=True,
            )

            related_docs = []
            for result in results.points:
                if result.payload and "documentation" in result.payload:
                    related_docs.append(
                        {
                            "documentation": result.payload["documentation"],
                            "similarity": result.score,
                        }
                    )

            return related_docs
        except Exception as e:
            logging.error(f"Error getting related documentation: {e}")
            return []

    def _add_training_data(self, text_to_embed: str, payload: dict, collection_name: str) -> str:
        """
        Generic private method to add training data to a Qdrant collection.

        Args:
            text_to_embed (str): The text to generate embeddings for.
            payload (dict): The payload to store with the vector.
            collection_name (str): The name of the Qdrant collection.

        Returns:
            str: The ID of the training data that was added, or an empty string on failure.
        """
        try:

            embedding = self.generate_embedding(text_to_embed)
            if not embedding:
                logging.error(f"Failed to generate embedding for text: {text_to_embed[:100]}...")
                return ""

            import uuid

            entry_id = f"{uuid.uuid4()}"

            self._client.upsert(
                collection_name=collection_name,
                points=[{"id": entry_id, "vector": embedding, "payload": payload}],
            )

            data_type = payload.get("type", "data")
            logging.info(f"Added {data_type} with ID: {entry_id}")
            return entry_id
        except Exception as e:
            data_type = payload.get("type", "data")
            logging.error(f"Error adding {data_type}: {e}")
            return ""

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """
        This method is used to add a question and its corresponding SQL query to the training data.

        Args:
            question (str): The question to add.
            sql (str): The SQL query to add.

        Returns:
            str: The ID of the training data that was added.
        """
        if not question or not sql:
            logging.error("Question or SQL cannot be empty")
            return ""

        payload = {"question": question, "sql": sql, "type": "sql"}

        return self._add_training_data(
            text_to_embed=question, payload=payload, collection_name=self.sql_collection_name
        )

    def add_ddl(self, ddl: str, **kwargs) -> str:
        """
        This method is used to add a DDL statement to the training data.

        Args:
            ddl (str): The DDL statement to add.

        Returns:
            str: The ID of the training data that was added.
        """
        if not ddl:
            logging.error("DDL cannot be empty")
            return ""

        payload = {"ddl": ddl, "type": "ddl"}

        return self._add_training_data(
            text_to_embed=ddl, payload=payload, collection_name=self.ddl_collection_name
        )

    def add_documentation(self, documentation: str, **kwargs) -> str:
        """
        This method is used to add documentation to the training data.

        Args:
            documentation (str): The documentation to add.

        Returns:
            str: The ID of the training data that was added.
        """
        if not documentation:
            logging.error("Documentation cannot be empty")
            return ""

        payload = {"documentation": documentation, "type": "documentation"}

        return self._add_training_data(
            text_to_embed=documentation,
            payload=payload,
            collection_name=self.documentation_collection_name,
        )

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """
        This method retrieves all training data from the single, unified Qdrant collection.
        It makes one efficient call and then parses the results based on the 'type'
        field stored in each point's payload.

        Returns:
            pd.DataFrame: A DataFrame containing all training data.
        """
        try:
            all_points, _ = self._client.scroll(
                collection_name=self.collection_name,
                limit=kwargs.get("limit", 1000),
                with_payload=True,
            )

            all_rows = []
            for point in all_points:
                payload = point.payload
                if not payload:
                    continue

                row = {
                    "id": point.id,
                    "type": payload.get("type", ""),
                    "question": "",
                    "sql": "",
                    "ddl": "",
                    "documentation": "",
                }

                if payload.get("type") == "sql":
                    row["question"] = payload.get("question", "")
                    row["sql"] = payload.get("sql", "")
                elif payload.get("type") == "ddl":
                    row["ddl"] = payload.get("ddl", "")
                elif payload.get("type") == "documentation":
                    row["documentation"] = payload.get("documentation", "")

                all_rows.append(row)

            return pd.DataFrame(all_rows)
        except Exception as e:
            logging.error(f"Error getting training data: {e}")
            return pd.DataFrame()

    def remove_training_data(self, id: str, **kwargs) -> bool:
        """
        Example:
        ```python
        vn.remove_training_data(id="123")
        ```

        This method is used to remove training data from the retrieval layer.

        Args:
            id (str): The ID of the training data to remove.

        Returns:
            bool: True if the training data was removed, False otherwise.
        """
        try:
            if not id:
                logging.error("ID cannot be empty")
                return False

            self._client.delete(collection_name=self.collection_name, points_selector=[id])

            logging.info(f"Removed training data with ID: {id}")
            return True
        except Exception as e:
            logging.error(f"Error removing training data: {e}")
            return False


qdrant_client = QdrantClient(url=QDRANT_URL)
vn = MyVanna(config={"client": qdrant_client})
vn.connect_to_postgres(
    host="localhost", dbname="chatbot", user="postgres", password="password", port="5432"
)


if __name__ == "__main__":
    print("Vanna CLI (type 'exit' to quit)")

    try:
        print("\nChecking training data...")
        training_data = vn.get_training_data()
        print(
            f"Training data available: {len(training_data) if training_data is not None else 'None'}"
        )
    except Exception as e:
        print(f"Failed to get training data: {e}")

    try:
        print("\nTesting database connection...")
        test_result = vn.run_sql("SELECT 1 as test")
        print(f"Database connection test: {'Success' if test_result is not None else 'Failed'}")
    except Exception as e:
        print(f"Database connection error: {e}")

    while True:
        question = input("\nAsk Vanna: ")
        if question.lower() == "exit":
            break

        print("\nNow trying the standard vn.ask() method:")
        try:
            response = vn.ask(question)
            print(f"vn.ask() response: {response}")
        except Exception as e:
            print(f"vn.ask() failed with error: {e}")
