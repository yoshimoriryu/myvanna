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

class MyVanna(Qdrant_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config={'api_key': GEMINI_API_KEY, 'model': GEMINI_MODEL})

# Setup Qdrant and Postgres
qdrant_client = QdrantClient(url=QDRANT_URL)
vn = MyVanna(config={'client': qdrant_client})
vn.connect_to_postgres(host='localhost', dbname='chatbot', user='postgres', password='password', port='5432')

if __name__ == "__main__":
    print("Vanna CLI (type 'exit' to quit)")
    while True:
        question = input("Ask Vanna: ")
        if question.lower() == "exit":
            break
        response = vn.ask(question)
        print("response: ", response)