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
├── domain_metadata.json          # **NEW**: Configuration for the Domain Router
├── docker-compose.yml            # Defines Postgres and Qdrant services
├── .env.example
├── pyproject.toml
└── README.md
```

<br>

## ⚙️ Features

-   **Multi-Agent Architecture**: Uses LangGraph to create a robust agentic system. A top-level **Routing Agent** analyzes user intent and dispatches tasks to specialized agents.
-   **Metadata-Driven Domain Routing**: The AI uses a configurable `domain_metadata.json` file with rich descriptions to accurately determine the correct data domain (e.g., `students`, `finance`) for a user's question.
-   **Secure, Air-Gapped Execution**: The Vanna/LLM agent **never** has direct access to the database. It generates SQL, which is then sent to a separate, secure FastAPI for execution.
-   **Idempotent Data Synchronization**: The `synchronizer.py` tool surgically syncs local training files with the Qdrant vector store.
-   **Clean & Decoupled**: Follows professional software design principles (`src` layout, externalized configuration).
-   **Automated & Isolated Testing**: A `run_tests.sh` script that spins up a dedicated, isolated test environment in Docker.

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

**A. Create `.env` file:**
Create a `.env` file from the `.env.example` and fill in your API keys.

**B. Create `domain_metadata.json` file:**
This file is **required** and configures the Domain Router. Create a `domain_metadata.json` file in the project root. For each domain you want to activate, add an entry with a concise, descriptive summary.

```json domain_metadata.json
{
    "students": "Contains data about student enrollment, courses, demographics, and academic status."
}
```

### 4️⃣ Train a Domain

For each domain defined in your metadata file, you must train it using the `run_training.sh` script.

**Example for the "students" domain:**
```bash
./scripts/run_training.sh students
```

### 5️⃣ Start Services (3 Terminals Required)

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
The chatbot will start and only load the domains that are present in both `domain_metadata.json` and Qdrant.

### 6️⃣ Run Integration Tests (Recommended)

Verify that the entire setup is working correctly with the automated test script.
```bash
./scripts/run_tests.sh
```

---

## 🧩 How It Works

The system operates as a sophisticated, multi-agent workflow orchestrated by LangGraph.

1.  **Intent Routing**: When a user sends a message, it first goes to an **Intent Router** to decide if the query is for the `GENERAL_CHAT` agent or the `SQL_AGENT`.

2.  **Domain Routing**: If the intent is `SQL_AGENT`, the query is passed to a **Domain Router**. This agent reads the `domain_metadata.json` file to create a rich prompt. It uses this context to analyze the user's question and decide which data domain is the most relevant.

3.  **SQL Generation**: The query is then passed to the appropriate `MyVanna` instance for that domain. The `vanna_engine` uses its RAG capabilities to generate a SQL query.

4.  **Secure Execution**: The generated SQL is passed to an **Execution Node** which first asks the user for approval, then calls the **Secure Execution API**.

5.  **Data Retrieval & Explanation**: The Secure API (the only component with DB credentials) executes the query and returns the results as JSON. This is passed to an **Explanation Node** which synthesizes a final, natural-language answer.
