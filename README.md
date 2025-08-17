# MyVanna: A Multi-Agent, Secure Data Chatbot

This project provides a production-ready, multi-agent implementation of Vanna AI, designed to answer questions securely against a private PostgreSQL database. It features a sophisticated, air-gapped architecture that separates the AI reasoning engine from the data execution engine.

-   **AI Orchestration**: LangGraph
-   **LLM & Embeddings**: Google Gemini
-   **Vector Store**: Qdrant (secured with an API key)
-   **Data Source**: PostgreSQL
-   **Environment Management**: Docker Compose

The system is organized into a reusable core engine, a secure execution API, a multi-agent chatbot application, an idempotent data synchronizer, and a full, multi-layered test suite.

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
│   ├── test_secure_api.py        # Integration tests for the secure API
│   └── test_chatbot_nodes.py     # Unit tests for the agent nodes using mocks
├── scripts/
│   ├── run_tests.sh              # Automated script to manage and run the test suite
│   └── run_training.sh           # Convenience script to run the data synchronizer
├── architecture.md               # **NEW**: Explains the secure, air-gapped architecture
├── domain_metadata.json          # Configuration for the Domain Router
├── docker-compose.yml            # Main Docker Compose for development
├── docker-compose-tests.yml      # Isolated Docker Compose for testing
├── .env.example                  # Example environment variables
├── .env.test                     # Overrides for the isolated test environment
├── pyproject.toml
└── README.md
```

<br>

## ⚙️ Features

-   **Multi-Agent Architecture**: Uses LangGraph to create a robust agentic system with intent and domain routing.
-   **Metadata-Driven Domain Routing**: Uses a configurable `domain_metadata.json` file with rich descriptions to accurately determine the correct data domain for a user's question.
-   **Secure, Air-Gapped Execution**: The Vanna/LLM agent **never** has direct access to the database. It generates SQL, which is then sent to a separate, secure FastAPI for execution. For more details, see the [**Architecture Guide**](docs/architecture.md).
-   **Production-Ready Configuration**: Dynamically constructs service URLs from their constituent parts (scheme, host, port), supporting both local HTTP and production HTTPS deployments.
-   **Automated & Isolated Testing**: A `run_tests.sh` script that spins up a dedicated, isolated test environment on separate ports using a `.env.test` file, preventing collisions with the development environment.

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
Create a `.env` file from the `.env.example`. This file configures the main development environment.

**B. Create `domain_metadata.json` file:**
This file is **required** and configures the Domain Router. Create a `domain_metadata.json` file in the project root. For each domain you want to activate, add an entry with a concise, descriptive summary.

```json domain_metadata.json
{
    "students": "Contains data about student enrollment, courses, demographics, and academic status."
}
```

**C. Review `.env.test`:**
This file (`.env.test`) is already configured to run the test environment on different ports (`5433`, `6334`) to avoid conflicts. You typically do not need to edit this file.

### 4️⃣ Train a Domain

For each domain defined in your metadata file, you must train it using the `run_training.sh` script.

**Example for the "students" domain:**
```bash
./scripts/run_training.sh students
```

### 5️⃣ Start Services (3 Terminals Required)

The full application runs as three separate processes.

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

### 6️⃣ Run Integration Tests (Recommended)

Verify that the entire setup is working correctly with the automated test script.
```bash
./scripts/run_tests.sh
```

---

## 🧩 How It Works

The system operates as a sophisticated, multi-agent workflow orchestrated by LangGraph.

1.  **Intent & Domain Routing**: A two-stage routing process first determines if a question is for the database, and if so, uses the `domain_metadata.json` to select the correct domain.

2.  **SQL Generation**: The query is passed to the appropriate `MyVanna` instance, which uses RAG to generate a SQL query.

3.  **Secure Execution**: The SQL is passed to an **Execution Node** which asks the user for approval, then calls the **Secure Execution API**. See the [**Architecture Guide**](architecture.md) for a detailed breakdown of this security model.

4.  **Data Retrieval & Explanation**: The Secure API executes the query and returns the results as JSON. This is passed to an **Explanation Node** which synthesizes a final, natural-language answer.