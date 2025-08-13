from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from vanna.google import GoogleGeminiChat
from training import ddl as defined_ddl, docs as defined_docs, sql as defined_sql
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-key")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
VANNA_COLLECTION_NAME = os.getenv("VANNA_COLLECTION_NAME", "myvanna_sql_collection")

class MyVanna(Qdrant_VectorStore, GoogleGeminiChat):
    def __init__(self, config):
        # Pass Qdrant-specific configs
        vector_config = {
            'client': config.get('qdrant_client'),
            'collection_name': config.get('collection_name', VANNA_COLLECTION_NAME),
        }

        # Pass Gemini-specific configs
        gemini_config = {
            'api_key': GEMINI_API_KEY,
            'model': GEMINI_MODEL
        }

        Qdrant_VectorStore.__init__(self, config=vector_config)
        GoogleGeminiChat.__init__(self, config=gemini_config)

# Setup Qdrant and Postgres
qdrant_client = QdrantClient(url=QDRANT_URL)
vn = MyVanna(config={'qdrant_client': qdrant_client, 'collection_name': VANNA_COLLECTION_NAME})
vn.connect_to_postgres(host='localhost', dbname='chatbot', user='postgres', password='password', port='5432')

# Training section =======================

# Concat DDL statements, documentation, and SQL training pairs
vn.train(ddl="\n".join(defined_ddl.ddl_statements))
vn.train(documentation="\n".join(defined_docs.documentation_texts))
sql_texts = "\n".join(
    f"question: {item['question']}\nanswer: {item['sql']}\n"
    for item in defined_sql.training_pairs
)
vn.train(sql=sql_texts)

training_data = vn.get_training_data()
print(training_data)
