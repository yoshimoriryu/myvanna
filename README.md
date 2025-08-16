# MyVanna: A Multi-Domain, Custom Vanna Implementation

This project provides a scalable, custom implementation of Vanna AI, designed to support multiple, isolated knowledge domains. It uses a clean, decoupled architecture with the following core components:
-   **LLM & Embeddings**: Google Gemini
-   **Vector Store**: Qdrant (secured with an API key)
-   **Data Source**: PostgreSQL
-   **Environment Management**: Docker Compose

The system is organized into a reusable Vanna engine, a generic command-line trainer, a multi-domain CLI, and a full integration test suite.

<br>

## 📂 Project Structure

```
.
├── main.py                     # CLI application that acts as a multi-domain Vanna factory
├── my_vanna.py                 # The reusable, configurable MyVanna class definition
├── config.py                   # Centralized configuration loader from environment variables
├── training.py                 # Generic CLI tool to train any Vanna domain
├── training_data/
│   └── students/               # Example domain for student data
│       ├── ddl.sql             # DDL statements for this domain
│       ├── docs.txt            # Documentation for this domain
│       └── sql.json            # SQL training pairs for this domain
├── tests/
│   └── test_integration_vanna.py # Pytest integration test suite
├── scripts/
│   └── run_tests.sh            # Automated script to run the test suite
├── docker-compose.yml          # Defines and configures the Postgres and Qdrant services
├── .env.example                # Example environment variables
├── pyproject.toml              # Poetry dependencies and project configuration
└── README.md
```

<br>

## ⚙️ Features

-   **Multi-Domain Architecture**: Manage multiple, isolated Vanna instances (e.g., for students, finance, HR), each with its own Qdrant collection.
-   **Dynamic Domain Discovery**: The main CLI application automatically discovers and loads all trained domains by querying the Qdrant vector store for collections matching the `vanna_*` naming convention.
-   **Clean & Decoupled**: Follows best practices like the Single Responsibility Principle and Dependency Injection.
    -   `my_vanna.py`: A reusable, self-contained Vanna engine.
    -   `config.py`: A single source of truth for configuration.
    -   `main.py` / `training.py`: Standalone applications that *use* the engine.
-   **Generic Command-Line Trainer**: A powerful `training.py` script that can train any domain by pointing it at the correct data files and collection name.
-   **User-Friendly CLI**: An interactive interface that allows users to select a domain and ask questions within that context.
-   **One-Command Environment**: Uses `docker-compose` to start, manage, and stop the entire stack (Postgres & Qdrant).
-   **Automated Testing**: A `run_tests.sh` script that brings up the environment, runs a full suite of integration tests, and tears it down automatically.

<br>

## 🚀 Getting Started

### 1️⃣ Prerequisites

-   Python 3.10+
-   [Poetry(https://python-poetry.org/)
-   [Docker](https://www.docker.com/) and Docker Compose

### 2️⃣ Install Dependencies

```bash
poetry install
```

### 3️⃣ Configure Environment

Create a `.env` file from the example. **Generate a secure Qdrant API key** (e.g., with `openssl rand -base64 32`).

```dotenv
# .env
# --- Qdrant ---
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY="your-super-secret-and-random-key-here"

# --- Google Gemini ---
GEMINI_API_KEY="your-gemini-api-key"

# --- Vanna Model Configuration (Defaults) ---
VANNA_MODEL="gemini-1.5-pro"
VANNA_EMBED_MODEL="models/embedding-001"

# --- PostgreSQL Connection (for Docker Compose and Vanna) ---
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="yourpassword"
POSTGRES_DB="chatbot"
```

### 4️⃣ Start Services

Start the Postgres and secure Qdrant containers in the background with a single command:
```bash
docker compose up -d
```

### 5️⃣ Prepare Training Data

Organize your training data into domain-specific subdirectories inside `training_data/`. For each domain (e.g., `students`), create:
1.  **`ddl.sql`**: A file containing all relevant `CREATE TABLE` statements.
2.  **`docs.txt`**: A plain text file where each line is a piece of documentation.
3.  **`sql.json`**: A JSON file containing an array of `{"question": "...", "sql": "..."}` objects.

### 6️⃣ Train a Domain

Use the generic `training.py` script to train a Vanna instance. You must specify the collection name and the paths to your data files.

**Example for the "students" domain:**
```bash
./scripts/run_training.sh <sub_folder on /training_data; ex: students>
```
Run this command for each domain you want to train, changing the `--collection-name` and file paths accordingly.

### 7️⃣ Run Integration Tests (Recommended)

Verify that your entire setup is working correctly with the automated test script. This will spin up a temporary environment, run tests, and tear it down.
```bash
./scripts/run_tests.sh
```

### 8️⃣ Run the Multi-Domain CLI

Start the main application. It will detect your trained domains and prompt you to choose one.
```bash
poetry run python main.py
```

---

## 🧩 How It Works

1.  **Configuration (`config.py`)**: This file loads all secrets and settings from the `.env` file, acting as the single source of truth for the entire application.

2.  **The Engine (`my_vanna.py`)**: This file defines the `MyVanna` class, a fully reusable and configurable component. It has no knowledge of the specific application using it and is configured entirely through the `config` dictionary passed to it during instantiation. It contains the core logic for all Vanna operations, including the `get_sql()` method.

3.  **Training (`training.py`)**: This is a command-line tool that takes a `--collection-name` (e.g., `vanna_students`) and data file paths as arguments. It creates a `MyVanna` instance configured for that specific collection and uses its `add_*` methods to populate the vector store. This is the only part of the system that needs access to the raw training data files.

4.  **The Application (`main.py`)**: This script acts as a "Vanna factory." It connects directly to Qdrant and discovers available domains by searching for collections with the `vanna_*` naming convention. For each collection found, it creates and configures a dedicated `MyVanna` instance, making Qdrant the single source of truth for what is "RAG-ready." It then presents a menu to the user, allowing them to select a domain and interact with the corresponding Vanna instance.

