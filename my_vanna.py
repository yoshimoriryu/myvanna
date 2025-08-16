from typing import List, Optional, Dict
import logging
import pandas as pd
from qdrant_client import QdrantClient
import google.generativeai as genai
import uuid

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

        print(f"Chat Model Initialized: {self.chat_model}")
        print(f"Embedding Model Initialized: {self.embedding_model}")

    def get_sql(self, question: str) -> Optional[str]:
        """
        Generates an SQL query for a given question without executing it.

        This method encapsulates the full Vanna logic:
        1. Retrieve relevant context (DDL, docs, SQL) from the vector store.
        2. Pass the context and question to the LLM to generate the SQL.

        Args:
            question: The user's question.

        Returns:
            The generated SQL query as a string, or None if generation fails.
        """
        logging.info("Step 1: Retrieving context from Qdrant...")
        ddl_context = self.get_related_ddl(question)
        docs_context = self.get_related_documentation(question)
        sql_context = self.get_similar_question_sql(question)

        ddl_strings = [item["ddl"] for item in ddl_context]
        doc_strings = [item["documentation"] for item in docs_context]
        sql_strings = [item["sql"] for item in sql_context]

        logging.info("Step 2: Generating SQL with Gemini...")
        return self.generate_sql(
            question=question,
            ddl_statements=ddl_strings,
            documentation=doc_strings,
            sql_examples=sql_strings,
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
        try:
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []

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
        try:
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []

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

    def _add_training_data(self, text_to_embed: str, payload: dict, **kwargs) -> str:
        try:
            embedding = self.generate_embedding(text_to_embed)
            if not embedding:
                logging.error(f"Failed to generate embedding for text: {text_to_embed[:100]}...")
                return ""

            entry_id = str(uuid.uuid4())

            self._client.upsert(
                collection_name=self.collection_name,
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
        if not question or not sql:
            logging.error("Question or SQL cannot be empty")
            return ""
        payload = {"question": question, "sql": sql, "type": "sql"}
        return self._add_training_data(text_to_embed=question, payload=payload)

    def add_ddl(self, ddl: str, **kwargs) -> str:
        if not ddl:
            logging.error("DDL cannot be empty")
            return ""
        payload = {"ddl": ddl, "type": "ddl"}
        return self._add_training_data(text_to_embed=ddl, payload=payload)

    def add_documentation(self, documentation: str, **kwargs) -> str:
        if not documentation:
            logging.error("Documentation cannot be empty")
            return ""
        payload = {"documentation": documentation, "type": "documentation"}
        return self._add_training_data(text_to_embed=documentation, payload=payload)

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

    def remove_training_data(self, id: str, **kwargs) -> bool:
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
