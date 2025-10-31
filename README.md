# MyVanna: A Multi-Agent, Secure Data Chatbot

This project is a smart chatbot that can answer questions about your data. It's built with a secure, air-gapped design that keeps the AI reasoning engine separate from the database execution engine, ensuring that the AI never has direct access to your data.

---

## Architecture Overview

The application is fully containerized using Docker Compose. A single command will launch the entire stack:

1.  **Database & Vector Store**: A PostgreSQL database for your data and a Qdrant vector database for the AI's long-term memory.
2.  **Secure SQL Executor API**: A simple, air-gapped FastAPI server (`secure_api`) that receives a SQL query, executes it, and returns the result.
3.  **Chatbot API**: The main user-facing FastAPI server (`chatbot_api`) containing the LangGraph agent, which handles the core AI logic.

This separation ensures maximum security, and Dockerization ensures a simple, one-step startup.

---

## 🚀 Quick Start Guide (Windows, macOS, & Linux)

The setup process is similar for all operating systems.

### Step 1: Install the Tools

1.  **Python**: [Download Python here](https://www.python.org/downloads/) (Version 3.10 or newer).
    *   On Windows, **check the box that says "Add Python to PATH"** during installation.
2.  **Docker Desktop**: [Download Docker here](https://www.docker.com/products/docker-desktop/). After installing, **start Docker Desktop** and let it run in the background.
3.  **Poetry** (For managing dependencies):
    *   **Windows (in PowerShell)**:
      ```powershell
      (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
      ```
    *   **macOS / Linux (in Terminal)**:
      ```bash
      curl -sSL https://install.python-poetry.org | python3 -
      ```

**Important**: After installing, **restart your Terminal or PowerShell window**.

### Step 2: Set Up the Project

1.  **Open your Terminal** (or PowerShell/CMD on Windows) and navigate to the project folder.
2.  **Configure Your API Key**:
    *   First, copy the example environment file.
      ```bash
      # On Windows CMD
      copy .env.example .env

      # On macOS/Linux/PowerShell
      cp .env.example .env
      ```
    *   Next, **get your Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Open the new `.env` file in a text editor and paste your key:
      ```
      GEMINI_API_KEY=your-api-key-goes-here
      ```
    *   Save and close the file.

### Step 3: Run the Application

This is the easy part. This single command builds the Docker images and starts all services at once.
```bash
docker-compose up --build
```
The first time you run this, it will take a few minutes to download and build everything. You will see logs from all the services in your terminal.

To run it in the background, you can add the `-d` flag: `docker-compose up --build -d`.

### Step 4: "Teach" the AI About Your Data

This one-time command populates the Qdrant vector database with your schema, documentation, and sample questions for the `students` domain. **Make sure your container is running.** Use `docker ps` command to see running containers.
```bash
docker exec -it myvanna-chatbot-api-1 python3 tools/synchronizer.py students
```
you can change `students` with <u>your domain</u>. Please make sure your naming is the same as folder you create at `training_data/` and add domain description at `domain_metada.json`.

After your training done, **restart chatbot-api** so they can load your new domain.
```bash
docker compose restart chatbot-api
```

### Step 4.5: Populate Dummy Database - No Production Database

We use dummy to not bother production database. This database simulate as production database which will receive vanna's sql query.
We need to "inject" database with dummies schema as follows,
```bash
chmod +x scripts/run_inject_schema.sh
./scripts/run_inject_schema.sh scripts/data/chatbot_schema.sql
```

### Step 5: Talk to the Chatbot!

1.  Open your web browser and go to: [http://localhost:8001/docs](http://localhost:8001/docs)
2.  You will see the FastAPI interface. Find the `/chat/` endpoint and click "Try it out".
3.  Ask a question in the `question` box. Try: `How many students are there?` (make sure `session_id` is empty or filled with past session_id)
4.  Click "Execute". You'll see the chatbot's response!

---
<br>

## ⚙️ Developer Guide: Training Workflow
After "Hello World" above, below is what you should do to increase Vanna's capability (New domain and/or changes on training_files/):

1. 🏗️ **Create a New Domain Directory**  
   Establish a new folder within `training_data/` and assign it an appropriate domain name (e.g., `<your_domain>`).  
   Note: Select a descriptive and meaningful name for proper organization and future reference.

2. 📝 **Update Domain Metadata**  
   Add an entry for `<your_domain>` in `domain_metadata.json` with an accurate description that corresponds to the domain's purpose and scope.  
   Ensure the description is clear and informative for future maintainability.

3. 📂 **Populate Training Data**  
   Provide the necessary training files in `training_data/<your_domain>` directory:  
   - `ddl.sql` – Database schema definitions
   - `docs.txt` – Documentation and contextual information
   - `sql.json` – Sample SQL queries and examples
   
   Reference the `training_data/students` directory for implementation examples.

4. 🔄 **Retrain After Modifications**  
   Execute the retraining process whenever changes are made to the training files to ensure Vanna incorporates the latest information.  
   Refer to [step 3](#step-4-teach-the-ai-about-your-data) for detailed retraining instructions.

5. 🏗️ **Initialize New Database Schemas**  
   When working with a dummy database and implementing a new schema, follow these procedures:  
   1. Place the DDL file in `scripts/data/ddl.sql` (rename appropriately to avoid overwriting existing files).
   2. Execute [step 4.5](#step-45-populate-dummy-database---no-production-database), substituting `chatbot_schema.sql` with your DDL filename.

6. 🎉 **Validation and Testing**  
   After completing the training workflow, interact with the chatbot and review the `generated_sql` output.  
   Verify that both the query syntax is correct and the returned data meets expected results to ensure system reliability.

# App Dev Details:
<details>
  <summary>Show more</summary>

## ⚙️ For App Developers: Detailed Guide
### Project Structure
```
.
├── docker-compose.yml            # Main Docker Compose to run the entire stack
├── Dockerfile.chatbot            # Dockerfile for the main Chatbot API
├── Dockerfile.secure_api         # Dockerfile for the Secure Executor API
├── src/
│   ├── chatbot/
│   │   └── agent.py              # Core LangGraph agent logic
│   └── vanna_engine/
│       ├── my_vanna.py           # The reusable, configurable Vanna engine
│       └── config.py             # Centralized configuration loader
├── secure_api/
│   └── main.py                   # Secure, air-gapped FastAPI for SQL execution
├── tools/
│   └── synchronizer.py           # Tool to sync training data to Qdrant
├── training_data/
│   └── ...                       # Folders for different data domains
└── pyproject.toml
```
### 

### Running Tests

To verify the system, run the automated test script. This will spin up an isolated test environment (using `docker-compose.test.yml`), run all tests, and then shut it down.
```bash
./scripts/run_tests.sh
```
