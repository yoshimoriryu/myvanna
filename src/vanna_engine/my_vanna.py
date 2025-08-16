from typing import List, Optional, Dict
import logging
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import google.generativeai as genai
import hashlib

from vanna.base import VannaBase
from vanna.google import GoogleGeminiChat
from vanna.qdrant import Qdrant_VectorStore


class MyVanna(Qdrant_VectorStore, GoogleGeminiChat):
    """
    Custom Vanna implementation using Google Gemini for generation and embeddings,
    and Qdrant as the vector store.
    """

    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = {}

        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("A Gemini API key must be provided in the config dictionary.")
        genai.configure(api_key=self.api_key)

        VannaBase.__init__(self, config=config)

        self.model_name = config.get("model", "gemini-1.5-pro")
        self.embedding_model = config.get("embedding_model", "models/embedding-001")
        self.temperature = float(config.get("temperature", 0.1))
        self.max_tokens = int(config.get("max_tokens", 2048))
        self.collection_name = config.get("collection_name", "myvanna_sql_collection")

        client = config.get("client")
        if client is None:
            q_url = config.get("qdrant_url", "http://localhost:6333")
            q_key = config.get("qdrant_api_key")
            client = QdrantClient(url=q_url, api_key=q_key)

        qdrant_store_config = {
            "client": client,
            "collection_name": self.collection_name,
            "documentation_collection_name": self.collection_name,
            "ddl_collection_name": self.collection_name,
            "sql_collection_name": self.collection_name,
        }

        gemini_config = {
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
        }

        Qdrant_VectorStore.__init__(self, config=qdrant_store_config)
        GoogleGeminiChat.__init__(self, config=gemini_config)

        logging.info(f"Chat Model Initialized: {self.chat_model}")
        logging.info(f"Embedding Model Initialized: {self.embedding_model}")

    def log(self, title: str, message: any):
        """
        Overrides the default VannaBase.log method to use the standard Python logger.
        Handles list-based messages for improved readability.
        """
        log_message = message
        # If the message is a list, join its elements with newlines for readability
        if isinstance(message, list):
            log_message = "\n".join(map(str, message))

        logging.info(f"{title}:\n{log_message}\n")

    def get_sql(self, question: str) -> Optional[str]:
        """
        Generates an SQL query for a given question without executing it.

        This method encapsulates the full Vanna logic:
        1. Retrieve relevant context (DDL, docs, SQL) from the vector store.
        2. Log the retrieved context for debugging purposes.
        3. Pass the context and question to the LLM to generate the SQL.
        """
        logging.debug("Step 1: Retrieving context from Qdrant...")
        ddl_context = self.get_related_ddl(question)
        docs_context = self.get_related_documentation(question)
        sql_context = self.get_similar_question_sql(question)

        # --- CONTEXT LOGGING - START ---
        logging.debug("\n--- Retrieved Context ---")
        if ddl_context:
            logging.debug(f"Found {len(ddl_context)} related DDL statements:")
            for item in ddl_context:
                logging.debug(f"  - {item['ddl']}")
        else:
            logging.debug("Found 0 related DDL statements.")

        if docs_context:
            logging.debug(f"Found {len(docs_context)} related documentation snippets:")
            for item in docs_context:
                logging.debug(f"  - {item['documentation']}")
        else:
            logging.debug("Found 0 related documentation snippets.")

        if sql_context:
            logging.debug(f"Found {len(sql_context)} similar SQL examples:")
            for item in sql_context:
                logging.debug(f"  - Question: {item['question']}")
                logging.debug(f"    SQL: {item['sql']}")
        else:
            logging.debug("Found 0 similar SQL examples.")
        logging.debug("-------------------------\n")
        # --- CONTEXT LOGGING - END ---

        ddl_strings = [item["ddl"] for item in ddl_context]
        doc_strings = [item["documentation"] for item in docs_context]
        sql_examples = [{"question": item["question"], "sql": item["sql"]} for item in sql_context]

        logging.info("Step 2: Generating SQL with Gemini...")
        return self.generate_sql(
            question=question,
            ddl_statements=ddl_strings,
            documentation=doc_strings,
            sql_examples=sql_examples,
        )

    def generate_embedding(self, text: str, **kwargs) -> List[float]:
        try:
            if not text or not isinstance(text, str):
                logging.warning(f"Invalid data for embedding: {text}")
                return []

            result = genai.embed_content(
                model=self.embedding_model, content=text, task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            return []

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        try:
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []

            sql_filter = Filter(must=[FieldCondition(key="type", match=MatchValue(value="sql"))])

            results = self._client.query_points(
                collection_name=self.sql_collection_name,
                query=question_embedding,
                query_filter=sql_filter,
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
        try:
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []

            ddl_filter = Filter(must=[FieldCondition(key="type", match=MatchValue(value="ddl"))])

            results = self._client.query_points(
                collection_name=self.ddl_collection_name,
                query=question_embedding,
                query_filter=ddl_filter,  # Apply the filter here
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
        try:
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []

            doc_filter = Filter(
                must=[FieldCondition(key="type", match=MatchValue(value="documentation"))]
            )

            results = self._client.query_points(
                collection_name=self.documentation_collection_name,
                query=question_embedding,
                query_filter=doc_filter,  # Apply the filter here
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

    def get_deterministic_id(self, text_to_embed: str) -> str:
        """
        Creates a stable, deterministic, and Qdrant-compatible UUID based on
        the hash of the content.
        """
        # Create a SHA256 hash of the content.
        sha256_hash = hashlib.sha256(text_to_embed.encode("utf-8")).hexdigest()

        # Take the first 32 characters of the hash (which is 128 bits, the same as a UUID)
        # and format it into the standard 8-4-4-4-12 UUID format. This is required
        # by Qdrant for string-based IDs.
        hash_as_uuid = f"{sha256_hash[0:8]}-{sha256_hash[8:12]}-{sha256_hash[12:16]}-{sha256_hash[16:20]}-{sha256_hash[20:32]}"

        return hash_as_uuid

    def _add_training_data(self, text_to_embed: str, payload: dict, entry_id: str, **kwargs) -> str:
        """
        Private method to upsert training data with a provided ID.
        "Upsert" means it will update the entry if the ID exists, or insert if it's new.
        """
        try:
            embedding = self.generate_embedding(text_to_embed)
            if not embedding:
                logging.error(f"Failed to generate embedding for text: {text_to_embed[:100]}...")
                return ""

            self._client.upsert(
                collection_name=self.collection_name,
                points=[{"id": entry_id, "vector": embedding, "payload": payload}],
            )

            data_type = payload.get("type", "data")
            logging.info(f"Upserted {data_type} with ID: {entry_id}")
            return entry_id
        except Exception as e:
            data_type = payload.get("type", "data")
            logging.error(f"Error upserting {data_type}: {e}")
            return ""

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        if not question or not sql:
            logging.error("Question or SQL cannot be empty")
            return ""
        payload = {"question": question, "sql": sql, "type": "sql"}
        # Use the question as the content for the ID
        entry_id = self.get_deterministic_id(question)
        return self._add_training_data(text_to_embed=question, payload=payload, entry_id=entry_id)

    def add_ddl(self, ddl: str, **kwargs) -> str:
        if not ddl:
            logging.error("DDL cannot be empty")
            return ""
        payload = {"ddl": ddl, "type": "ddl"}
        entry_id = self.get_deterministic_id(ddl)
        return self._add_training_data(text_to_embed=ddl, payload=payload, entry_id=entry_id)

    def add_documentation(self, documentation: str, **kwargs) -> str:
        if not documentation:
            logging.error("Documentation cannot be empty")
            return ""
        payload = {"documentation": documentation, "type": "documentation"}
        entry_id = self.get_deterministic_id(documentation)
        return self._add_training_data(
            text_to_embed=documentation, payload=payload, entry_id=entry_id
        )

    def get_training_data(self, **kwargs) -> pd.DataFrame:
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

    def get_all_training_data_ids(self, **kwargs) -> List[str]:
        """
        Efficiently retrieves all training data point IDs from the collection.

        Returns:
            A list of all unique IDs currently in the collection.
        """
        try:
            # Scroll through all points in the collection, but only fetch the IDs.
            # This is much more efficient than fetching the full payload and vectors.
            all_points, _ = self._client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust if you expect more than 10,000 training entries
                with_payload=False,
                with_vectors=False,
            )
            return [point.id for point in all_points]
        except Exception as e:
            logging.error(f"Error getting all training data IDs: {e}")
            return []

    def remove_training_data(self, ids: List[str], **kwargs) -> bool:
        """
        Removes a list of training data entries from the retrieval layer by their IDs.
        """
        try:
            if not ids:
                logging.warning("No IDs provided for removal.")
                return True  # Nothing to do, so it's a success.

            # The delete method expects a list of IDs
            self._client.delete(collection_name=self.collection_name, points_selector=ids)
            logging.info(f"Removed {len(ids)} training data entries.")
            return True
        except Exception as e:
            logging.error(f"Error removing training data: {e}")
            return False
