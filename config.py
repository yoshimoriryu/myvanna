import os
from dotenv import load_dotenv

load_dotenv()

# --- Gemini Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Vanna Model Configuration ---
VANNA_MODEL = os.getenv("VANNA_MODEL", "gemini-1.5-pro")
VANNA_EMBED_MODEL = os.getenv("VANNA_EMBED_MODEL", "models/embedding-001")
VANNA_TEMPERATURE = float(os.getenv("VANNA_TEMPERATURE", 0.1))
VANNA_MAX_TOKENS = int(os.getenv("VANNA_MAX_TOKENS", 2048))

# --- Qdrant Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
VANNA_COLLECTION_NAME = os.getenv("VANNA_COLLECTION_NAME", "myvanna_sql_collection")

# --- PostgreSQL Connection ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "chatbot")

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Pre-flight Checks ---
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# --- Configuration Dictionary ---
# This dictionary is created from the module-level constants above.
# It provides a convenient way to pass the entire configuration to classes
# or functions, while still allowing for static analysis and autocomplete
# when importing the 'config' module directly (e.g., config.QDRANT_URL).
VANNA_CONFIG_DICT = {
    "api_key": GEMINI_API_KEY,
    "model": VANNA_MODEL,
    "embedding_model": VANNA_EMBED_MODEL,
    "temperature": VANNA_TEMPERATURE,
    "max_tokens": VANNA_MAX_TOKENS,
    "collection_name": VANNA_COLLECTION_NAME,
    "qdrant_url": QDRANT_URL,
    "qdrant_api_key": QDRANT_API_KEY,
}
