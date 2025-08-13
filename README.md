# FastAPI Boilerplate

This is a boilerplate project for building APIs using FastAPI. It provides a basic structure to get started quickly and uses [Poetry](https://python-poetry.org/) for dependency management.

## Project Structure

```
myvanna
├── app
│   ├── main.py          # Entry point of the FastAPI application
│   ├── api
│   │   └── endpoints.py # API endpoints definition
│   ├── models
│   │   └── __init__.py  # Data models (currently empty)
│   └── schemas
│       └── __init__.py  # Request and response schemas (currently empty)
├── pyproject.toml       # Poetry configuration file
├── README.md            # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd myvanna
   ```

2. **Install Poetry (if not already installed):**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Run the application:**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Usage

Once the application is running, you can access the API at `http://127.0.0.1:8000/`.  
The root endpoint (`/`) will return a simple JSON response:

```json
{"message": "Hello from FastAPI!"}
```

## License

This project is licensed under the MIT License.