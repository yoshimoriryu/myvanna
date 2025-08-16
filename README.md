# MyVanna Custom Implementation

An example of a custom Vanna AI implementation that uses **Google Gemini** for embeddings and generation, **Qdrant** as the vector store, and connects to a **PostgreSQL** database.

This project includes a one-time training script, a CLI for asking questions, and a full integration test suite using `pytest`.

<br>

## 📂 Project Structure

```
.
├── main.py                     # Main application, Vanna class, and CLI entry point
├── training.py                 # Script to perform one-time training
├── training_data/
│   ├── sql.py                  # Contains SQL training pairs
│   ├── docs.py                 # Contains documentation text
│   └── dddl.py                 # Contains DDL statements
├── tests/
│   └── test_integration_vanna.py # Integration tests for the MyVanna class
├── .env.example                # Example environment variables
├── .gitignore
├── pyproject.toml              # Poetry configuration & dependencies
└── README.md
```

<br>

## ⚙️ Features

-   **Custom Vanna Class**: `MyVanna` inherits from Vanna's base classes to provide a custom implementation of all required abstract methods.
-   **Gemini Integration**: Uses Google Gemini for both generating SQL and creating embeddings.
-   **Qdrant Vector Store**: All training data (DDL, documentation, and SQL examples) is embedded and stored in a Qdrant collection.
-   **One-Time Training**: A simple script to populate the vector store with your custom data.
-   **Interactive CLI**: A command-line interface to ask questions and get SQL answers from your trained model.
-   **Integration Test Suite**: Uses `pytest` to verify that all components (Gemini, Qdrant, Postgres) are working together correctly.

<br>

## 🚀 Getting Started

### 1️⃣ Prerequisites

-   Python 3.10+
-   [Poetry](https://python-poetry.org/) for dependency management.
-   [Docker](https://www.docker.com/) for running Postgres and Qdrant.

### 2️⃣ Install Dependencies

Clone the repository and install the required packages using Poetry:

```bash
poetry install
```

### 3️⃣ Environment Variables

Create a `.env` file in the project root. You can copy the `.env.example` file to get started.

```env
# --- Qdrant ---
QDRANT_URL="http://localhost:6333"

# --- Google Gemini ---
GEMINI_API_KEY="your-gemini-api-key"

# --- Vanna Model Configuration ---
# The model used for generating SQL (e.g., "gemini-1.5-pro", "gemini-1.5-flash")
VANNA_MODEL="gemini-1.5-pro"
# The model used for creating embeddings (e.g., "models/embedding-001")
VANNA_EMBED_MODEL="models/embedding-001"
VANNA_COLLECTION_NAME="myvanna_sql_collection"

# --- PostgreSQL Connection (for Vanna to connect to your data) ---
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="yourpassword"
POSTGRES_DB="chatbot"
```

### 4️⃣ Start Services (via Docker)

**Start Qdrant:**
```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

**Start PostgreSQL:**
(Make sure the password matches your `.env` file)
```bash
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=chatbot \
  -p 5432:5432 \
  postgres:17
```

### 5️⃣ Train the Model

Run the one-time training script. This will read the files in `training_data/`, generate embeddings, and store them in your Qdrant collection.

```bash
poetry run python training.py
```

### 6️⃣ Run the Integration Tests (Optional but Recommended)

This project includes a script that automatically starts the required Docker services, runs the test suite, and tears them down afterward.

From the project root, simply run:
```bash
./scripts/run_tests.sh

### 7️⃣ Run the CLI

Start the interactive command-line interface to begin asking questions.

```bash
poetry run python main.py
```

---

## 🧩 How It Works

1.  **Custom Class (`MyVanna`)**: The `main.py` file defines a `MyVanna` class that inherits from `vanna.Qdrant_VectorStore` and `vanna.GoogleGeminiChat`. It implements all the abstract methods required by Vanna's base classes, such as `add_ddl`, `get_related_ddl`, etc., using custom logic tailored for Qdrant and Gemini.

2.  **Training Phase**: The `training.py` script imports the `MyVanna` instance and calls the custom `add_ddl`, `add_documentation`, and `add_question_sql` methods. These methods use the Gemini API to create vector embeddings and then store them in the specified Qdrant collection.

3.  **Query Phase**: When you run `main.py` and ask a question, Vanna's `ask()` method orchestrates the process. It calls the custom `get_related_*` methods to retrieve relevant context (DDL, docs, SQL examples) from Qdrant. This context is then passed to the Gemini chat model to generate the final SQL query.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🧠 References

-   [Vanna AI Docs](https://vanna.ai/docs)
-   [Qdrant Docs](https://qdrant.tech/documentation/)
-   [Gemini API Docs](https://ai.google.dev/docs)
-   [Pytest Docs](https://docs.pytest.org/)
