import pytest
from fastapi.testclient import TestClient
import sys
import os

from secure_api.main import app

# The TestClient is a special object from FastAPI for testing
client = TestClient(app)


def test_execute_sql_success():
    """
    Tests the "happy path": executing a valid, safe SQL query.
    """
    print("\n--- Testing API: Successful SELECT query ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "SELECT 1 as id, 'test' as name;"},
    )
    # Assert we get a 200 OK status
    assert response.status_code == 200
    # Assert the response is the correct JSON data
    assert response.json() == [{"id": 1, "name": "test"}]
    print("Success path test passed.")


def test_execute_sql_security_rejection():
    """
    Tests the CRITICAL security path: ensuring the API rejects dangerous keywords.
    """
    print("\n--- Testing API: Security rejection for DELETE query ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "DELETE FROM students;"},
    )
    # Assert we get a 403 Forbidden status
    assert response.status_code == 403
    # Assert the error message is correct
    assert "forbidden" in response.json()["detail"].lower()
    print("Security rejection test passed.")


def test_execute_sql_invalid_syntax():
    """
    Tests the error handling path: sending a query with a syntax error.
    """
    print("\n--- Testing API: Error handling for invalid SQL ---")
    response = client.post(
        "/execute-sql",
        json={"sql": "SELECT FROM students WHERE;"},
    )
    # Assert we get a 400 Bad Request status, as the database will reject it
    assert response.status_code == 400
    # Assert the error message indicates a database-level error
    assert "Error executing SQL" in response.json()["detail"]
    print("Invalid syntax test passed.")
