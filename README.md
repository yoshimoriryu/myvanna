# MyVanna: A Multi-Agent, Secure Data Chatbot

This project provides a production-ready, multi-agent implementation of Vanna AI, designed to answer questions securely against a private PostgreSQL database. It features a sophisticated, air-gapped architecture that separates the AI reasoning engine from the data execution engine.

-   **AI Orchestration**: LangGraph
-   **LLM & Embeddings**: Google Gemini
-   **Vector Store**: Qdrant (secured with an API key)
-   **Data Source**: PostgreSQL
-   **Environment Management**: Docker Compose

The system is organized into a reusable core engine, a secure execution API, a multi-agent chatbot application, an idempotent data synchronizer, and a full integration test suite.

<br>

## 📂 Project Structure

The project follows a standard `src` layout to cleanly separate the core library from the applications that use it.

```
.
├── apps/
│   ├── multi_agent_chatbot.py    # The main LangGraph-powered chatbot application
│   └── synchronizer.py           # Idempotent tool to sync training data to Qdrant
├── src/
│   └── vanna_engine/
│       ├── __init__.py           # Makes the engine an installable package
│       ├── my_vanna.py           # The reusable, configurable MyVanna engine/class
│       └── config.py             # Centralized configuration loader from .env
├── secure_api/
│   └── main.py                   # Secure, air-gapped FastAPI for SQL execution
├── training_data/
│   └── students/                 # Example domain for student data
│       ├── ddl.sql
│       ├── docs.txt
│       └── sql.json
├── tests/
│   ├── test_integration_vanna.py # Tests for the core vanna_engine
│   └── test_secure_api.py        # Tests for the secure execution API
├── scripts/
│   ├── run_tests.sh              # Automated script to manage and run the test suite
│   └── run_training.sh           # Convenience script to run the data synchronizer
├── docker-compose.yml            # Defines Postgres and Qdrant services
├── .env.example
├── pyproject.toml
└── README.md
```

<br>

## ⚙️ Features

-   **Multi-Agent Architecture**: Uses LangGraph to create a robust agentic system. A top-level **Routing Agent** analyzes user intent and dispatches tasks to specialized agents (e.g., a SQL Agent or a General Chat Agent).
-   **Automatic Domain Routing**: The AI automatically determines the correct data domain (e.g., `students`, `finance`) for a user's question, providing a seamless user experience.
-   **Secure, Air-Gapped Execution**: The Vanna/LLM agent **never** has direct access to the database. It generates SQL, which is then sent to a separate, secure FastAPI for execution, following enterprise-grade security best practices.
-   **Idempotent Data Synchronization**: The `synchronizer.py` tool doesn't just add data; it surgically syncs the state of local training files with the Qdrant vector store, performing additions, updates, and deletions as needed.
-   **Clean & Decoupled**: Follows professional software design principles (`src` layout, dependency management via Poetry, centralized configuration).
-   **One-Command Environment**: Uses `docker-compose` to start, manage, and stop the entire infrastructure stack (Postgres & Qdrant).
-   **Automated & Isolated Testing**: A `run_tests.sh` script that spins up a dedicated, isolated test environment in Docker, runs the full test suite, and tears it down automatically.

<br>

## 🚀 Getting Started

### 1️⃣ Prerequisites

-   Python 3.10+
-   [Poetry](https://python-poetry.org/)
-   [Docker](https://www.docker.com/) and Docker Compose

### 2️⃣ Install Dependencies

```bash
poetry install
```

### 3️⃣ Configure Environment

Create a `.env` file from the `.env.example`. **Generate a secure Qdrant API key** (e.g., with `openssl rand -base64 32`).

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
ROUTER_AGENT_MODEL="gemini-pro" # Optional: Specify a different model for the router

# --- PostgreSQL Connection (for Docker Compose and Secure API) ---
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="yourpassword"
POSTGRES_DB="chatbot"
```

### 4️⃣ Start Services (3 Terminals Required)

The full application runs as three separate processes. You will need to open three terminals in the project's root directory.

**Terminal 1: Start Infrastructure**
```bash
docker compose up -d
```

**Terminal 2: Start the Secure Execution API**
```bash
poetry run uvicorn secure_api.main:app --reload
```

**Terminal 3: Start the Multi-Agent Chatbot**
```bash
poetry run python apps/multi_agent_chatbot.py
```

### 5️⃣ Train a Domain

Before you can chat, you must train at least one domain. Use the `run_training.sh` convenience script, passing it the name of a subdirectory in `training_data/`.

**Example for the "students" domain:**
```bash
./scripts/run_training.sh students
```
The chatbot application will automatically detect any trained domains when it starts.

### 6️⃣ Run Integration Tests (Recommended)

Verify that the entire setup is working correctly with the automated test script. This is the **safest way to test**, as it uses a dedicated, temporary environment.
```bash
./scripts/run_tests.sh
```

---

## 🧩 How It Works

The system operates as a sophisticated, multi-agent workflow orchestrated by LangGraph.

1.  **Intent Routing**: When a user sends a message, it first goes to an **Intent Router**. This agent uses an LLM to decide if the query is a general conversational question (`GENERAL_CHAT`) or if it requires database access (`SQL_AGENT`).

2.  **Domain Routing**: If the intent is `SQL_AGENT`, the query is passed to a **Domain Router**. This agent analyzes the question and decides which data domain (e.g., `students`, `finance`) is the most relevant, based on the domains that have been trained.

3.  **SQL Generation**: The query is then passed to the appropriate `MyVanna` instance for that domain. The `vanna_engine` uses its RAG capabilities to generate a SQL query based on the DDL, documentation, and SQL pairs it was trained on.

4.  **Secure Execution**: The generated SQL is **not** executed by the agent. Instead, it is passed to an **Execution Node** in the LangGraph flow. This node performs two critical functions:
    a.  **User Approval**: It presents the SQL to the user for approval—a vital safety check.
    b.  **API Call**: Upon approval, it sends the SQL query via an HTTP request to the standalone **Secure Execution API**.

5.  **Data Retrieval**: The Secure API is the only component with direct database credentials. It receives the SQL, runs it against the private PostgreSQL database, and returns the results as JSON.

6.  **Explanation**: The JSON result is passed back to the LangGraph agent, which sends the original question and the data to an **Explanation Node**. This node uses an LLM to synthesize a final, natural-language answer for the user.
