# MyVanna CLI

A simple CLI wrapper around [Vanna AI](https://vanna.ai/) that performs **one-time training** on your own SQL, documentation, and database schema.  
This project uses **Gemini** for embeddings, **Qdrant** as the vector store, and **PostgreSQL** for the database.

<br>

## 📂 Project Structure

```
.
├── main.py               # Entry point for running the CLI
├── training.py           # Script to perform one-time training
├── training/
│   ├── sql.py            # Contains SQL training pairs
│   ├── docs.py           # Contains documentation text
│   ├── ddl.py            # Contains DDL statements
├── pyproject.toml        # Poetry configuration & dependencies
└── README.md
```

<br>

## ⚙️ Features

- **One-time training** of a Vanna instance using:
  - SQL examples (`training/sql.py`)
  - Documentation text (`training/docs.py`)
  - Database DDL schema (`training/ddl.py`)
- Stores embeddings in **Qdrant**.
- Uses **Google Gemini** for LLM + embeddings.
- Simple CLI interface for interacting with your trained model.

<br>

## 🚀 Getting Started

### 1️⃣ Install Dependencies

This project uses [Poetry](https://python-poetry.org/):

```bash
poetry install
```

---

### 2️⃣ Environment Variables

Create a `.env` file in the project root:

```env
# Qdrant
QDRANT_URL=http://localhost:6333

# Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# Postgres
POSTGRES_URL=postgresql://postgres:yourpassword@localhost:5432/chatbot
```

## Running Postgres with Docker

If you don’t have Postgres installed locally, you can run it in a Docker container:

```bash
docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=chatbot -p 5432:5432 postgres:17
```

**Explanation of parameters:**
- `POSTGRES_USER` — database username (default: `postgres`)
- `POSTGRES_PASSWORD` — password for the user
- `POSTGRES_DB` — name of the initial database (in this case, `chatbot`)
- `-p 5432:5432` — maps the container’s Postgres port to your local machine

Once running, you can connect using:

```bash
psql -h localhost -p 5432 -U postgres -d chatbot
```

Enter the password you set with `POSTGRES_PASSWORD`.

**.env example:**
```
POSTGRES_URL=postgresql://postgres:yourpassword@localhost:5432/chatbot
```

---

### 3️⃣ Start Qdrant (via Docker)

```bash
docker run -d   --name qdrant   -p 6333:6333   qdrant/qdrant
```

---

### 4️⃣ Train the Model

Run **one-time training**:

```bash
poetry run python training.py
```

This will:
- Load SQL examples, docs, and DDL from `training/`
- Embed the data via Gemini
- Store it in Qdrant

---

### 5️⃣ Run the CLI

```bash
poetry run python main.py
```

Type your question, and Vanna will respond with relevant SQL queries.

---

## 🧩 How It Works

1. **Training Phase**  
   - Reads data from `training/`  
   - Calls `vanna.train(...)` with:
     - Documentation text
     - SQL question-answer pairs
     - Database schema (DDL)  
   - Data is embedded with **Gemini** and stored in **Qdrant**.

2. **Query Phase**  
   - You type a question in the CLI  
   - Vanna retrieves the most relevant context from Qdrant  
   - Generates SQL using Gemini

---

## 📜 License

MIT License. Free to use and modify.

---

## 🧠 References

- [Vanna AI Docs](https://vanna.ai/docs)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Gemini API Docs](https://ai.google.dev/docs)
