# MyVanna: A Multi-Agent, Secure Data Chatbot

This project is a smart chatbot that can answer questions about your data. It's built with a secure, air-gapped design that keeps the AI reasoning engine separate from the database execution engine.

---

## 🚀 Windows Quick Start Guide (for Absolute Beginners)

If you are using Windows and have never coded before, this guide is for you! Follow these steps exactly.

### Step 1: Install the Tools

First, you need to install three programs on your computer.

1.  **Python**: [Download Python here](https://www.python.org/downloads/) (Version 3.10 or newer). **Important:** During installation, make sure to check the box that says **"Add Python to PATH"**.
2.  **Docker Desktop**: [Download Docker here](https://www.docker.com/products/docker-desktop/). This runs our database. After installing, start Docker Desktop and let it run.
3.  **Poetry**: This tool manages the Python libraries.
    *   Open a terminal called **PowerShell** (search for it in your Start Menu).
    *   Copy and paste the following command into PowerShell and press Enter:
      ```powershell
      (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
      ```

**Important**: After installing everything, **restart your computer** to make sure all the commands are available.

### Step 2: Open a Terminal in the Project Folder

This is a critical step. We need to run commands from inside the project folder.

1.  Open the **File Explorer** (the yellow folder icon on your taskbar).
2.  Navigate to the folder where you unzipped or downloaded the project code.
3.  Click once in the **address bar** at the top of the File Explorer window. The path (e.g., `C:\Users\YourName\Downloads\MyVanna-main`) will turn blue.
4.  Type the word `cmd` directly into the address bar and press **Enter**. (Yes, you replace the address bar with your typed `cmd`)

A black terminal window will pop up. It will already be running inside your project folder! **All the following commands must be run in this new window.**

### Step 3: Set Up the Project

Now, with your new terminal window open, let's get the project ready.

**A. Install Python Libraries**
Run this command to download all the necessary code libraries.
```cmd
poetry install
```

**B. Configure Your API Key**
The chatbot uses Google's Gemini AI. You need to give it your secret API key.

1.  Make a copy of the example file by running this command:
    ```cmd
    copy .env.example .env
    ```
2.  **Get your Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
3.  Open the project folder in File Explorer and find the new `.env` file. Open it with **Notepad**.
4.  Paste your key into this line:
    ```
    GEMINI_API_KEY=your-api-key-goes-here
    ```
    Save and close the file.

### Step 4: "Teach" the AI About Your Data

This command loads the information about the `students` database into the AI's memory.
```cmd
poetry run python tools/synchronizer.py students
```

### Step 5: Run the Application (You need 3 Terminals!)

The application runs in three parts. You must open **three separate Command Prompt windows**, all in the project folder (repeat Step 2 to open new ones). Run one command in each and leave them running.

**Terminal 1️⃣: Start the Database**
```cmd
docker-compose up
```
*You will see a lot of log messages. Just leave this terminal running.*

**Terminal 2️⃣: Start the Secure API**
```cmd
poetry run python run_api.py
```
*Leave this terminal running.*

**Terminal 3️⃣: Start the Chatbot**
```cmd
poetry run python run_cli.py
```

### Step 6: Talk to the Chatbot!

If everything worked, you will see a message in Terminal 3 that says `--- Starting Chat ---`.

You can now ask it questions about the data! Try this one:
`How many students are there?`

Congratulations, you have the project running!

---
<br>

## 🍎 Linux & macOS Quick Start

This guide is for users on Linux or macOS systems.

1.  **Install Tools**: Ensure you have Python 3.10+, Docker, and Poetry installed.
2.  **Install Dependencies**: `poetry install`
3.  **Configure**: `cp .env.example .env` and add your `GEMINI_API_KEY`.
4.  **Train**: `./scripts/run_training.sh students`
5.  **Run**: Open three terminals and run the following commands:
    *   **Terminal 1**: `docker-compose up`
    *   **Terminal 2**: `poetry run python run_api.py`
    *   **Terminal 3**: `poetry run python run_cli.py`

---
<br>

## ⚙️ For Developers: Detailed Guide

### Project Structure

```
.
├── docs/
│   ├── architecture.md           # Diagram and explanation of the secure architecture
│   └── PRD.md                    # Project Requirements Document
├── src/
│   ├── chatbot/
│   │   └── agent.py              # Core LangGraph agent logic
│   └── vanna_engine/
│       ├── my_vanna.py           # The reusable, configurable Vanna engine
│       └── config.py             # Centralized configuration loader from .env
├── secure_api/
│   └── main.py                   # Secure, air-gapped FastAPI for SQL execution
├── tools/
│   └── synchronizer.py           # Idempotent tool to sync training data to Qdrant
├── training_data/
│   ├── students/                 # Example domain for student data
│   ├── faculty/                  # Example domain for faculty data
│   └── ...
├── tests/
│   ├── test_integration_vanna.py # Tests for the core vanna_engine
│   ├── test_secure_api.py        # Integration tests for the secure API
│   └── test_chatbot_nodes.py     # Unit tests for the agent nodes
├── scripts/
│   ├── run_tests.sh              # Automated script to manage and run the test suite
│   └── run_training.sh           # Convenience script for the synchronizer
├── run_api.py                    # Entry point to run the Secure API
├── run_cli.py                    # Entry point to run the Chatbot
├── domain_metadata.json          # Configuration for the Domain Router
├── docker-compose.yml            # Main Docker Compose for development
└── pyproject.toml
```

### Advanced Configuration

-   **Multiple Domains**: To add a new domain (e.g., `faculty`), create a new folder under `training_data/` and populate it with `ddl.sql`, `docs.txt`, and `sql.json`. Then, update `domain_metadata.json` with a description for the new domain and train it with `./scripts/run_training.sh faculty` (or `poetry run python tools/synchronizer.py faculty` on Windows).
-   **Test Environment**: The `.env.test` file is pre-configured to run services on alternate ports to avoid conflicts. The `run_tests.sh` script handles the setup and teardown of this environment automatically.

### Running Tests

To verify the entire system, run the automated test script. This will spin up the isolated test environment, run all tests, and then shut the environment down.
```bash
./scripts/run_tests.sh
```