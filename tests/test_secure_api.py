import pytest
from fastapi.testclient import TestClient
from secure_api.main import app


# --- NEW: Create the client inside a fixture ---
# This function will be run FOR EACH test that uses it, ensuring a fresh client
# with a valid database connection every time.
@pytest.fixture
def client():
    # The 'with' statement ensures the client is properly shut down
    with TestClient(app) as c:
        yield c


# --- MODIFIED: Each test now accepts the 'client' fixture as an argument ---
def test_execute_sql_success(client):
    """
    Tests the "happy path": executing a valid, safe SQL query.
    """
    print("\n--- Testing API: Successful SELECT query ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "SELECT 1 as id, 'test' as name;"},
    )
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "test"}]
    print("Success path test passed.")


def test_execute_sql_security_rejection(client):
    """
    Tests the CRITICAL security path: ensuring the API rejects dangerous keywords.
    """
    print("\n--- Testing API: Security rejection for DELETE query ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "DELETE FROM students;"},
    )
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()
    print("Security rejection test passed.")


def test_execute_sql_invalid_syntax(client):
    """
    Tests the error handling path: sending a query with a syntax error.
    """
    print("\n--- Testing API: Error handling for invalid SQL ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "SELECT FROM students WHERE;"},
    )
    assert response.status_code == 400
    assert "Error executing SQL" in response.json()["detail"]
    print("Invalid syntax test passed.")
