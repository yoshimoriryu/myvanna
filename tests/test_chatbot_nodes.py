import pytest
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage


from apps.multi_agent_chatbot import (
    GraphState,
    intent_router_node,
    domain_router_node,
    generate_sql_node,
    execute_sql_node,
    # We will test the other nodes in a similar fashion
)


# A sample initial state that we can reuse for multiple tests
@pytest.fixture
def initial_state():
    return GraphState(
        messages=[HumanMessage(content="How many students are there?")],
        next_tool="",
        vanna_domain="",
        sql_query=None,
        query_result=None,
        explanation=None,
        error_message=None,
    )


def test_intent_router_node_routes_to_sql(mocker, initial_state):
    """
    Tests that the intent_router correctly identifies a SQL-related question.
    """
    print("\n--- Testing Node: intent_router (SQL path) ---")
    # Mock the GenerativeModel call to control the AI's output
    mock_model = MagicMock()
    # Configure the mock response object
    mock_response = MagicMock()
    mock_response.text = "SQL_AGENT"
    mock_model.generate_content.return_value = mock_response
    # This is the core of mocking: patch the real object with our fake one
    mocker.patch("apps.multi_agent_chatbot.genai.GenerativeModel", return_value=mock_model)

    # Run the node with our initial state
    result = intent_router_node(initial_state)

    # Assert that the correct decision was made
    assert result == {"next_tool": "SQL_AGENT"}
    # Verify that our mock LLM was actually called
    mock_model.generate_content.assert_called_once()
    print("Intent router SQL path test passed.")


def test_domain_router_node_selects_domain(mocker, initial_state):
    """
    Tests that the domain_router correctly selects a domain from the available list.
    """
    print("\n--- Testing Node: domain_router ---")
    # Mock the global list of available domains
    mocker.patch("apps.multi_agent_chatbot.AVAILABLE_DOMAINS", ["students", "finance"])

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "students"  # Simulate the LLM choosing 'students'
    mock_model.generate_content.return_value = mock_response
    mocker.patch("apps.multi_agent_chatbot.genai.GenerativeModel", return_value=mock_model)

    result = domain_router_node(initial_state)

    assert result == {"vanna_domain": "students"}
    mock_model.generate_content.assert_called_once()
    print("Domain router test passed.")


def test_generate_sql_node_success(mocker, initial_state):
    """
    Tests the happy path for the SQL generation node.
    """
    print("\n--- Testing Node: generate_sql (Success path) ---")
    # Mock the MyVanna instance and its get_sql method
    mock_vanna = MagicMock()
    mock_vanna.get_sql.return_value = "SELECT COUNT(*) FROM students;"
    # Mock the global dictionary that holds the Vanna instances
    mocker.patch("apps.multi_agent_chatbot.VANNA_INSTANCES", {"students": mock_vanna})

    # Set the domain in the state so the node knows which mock instance to use
    initial_state["vanna_domain"] = "students"

    result = generate_sql_node(initial_state)

    assert result == {"sql_query": "SELECT COUNT(*) FROM students;"}
    mock_vanna.get_sql.assert_called_with("How many students are there?")
    print("Generate SQL success path test passed.")


def test_execute_sql_node_user_approves(mocker):
    """
    Tests the execution node when the user approves and the API call is successful.
    """
    print("\n--- Testing Node: execute_sql (User Approval path) ---")
    # Mock the user input to simulate them typing 'y' and pressing Enter
    mocker.patch("builtins.input", return_value="y")

    # Mock the requests.post call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"count": 100}]
    mock_response.raise_for_status.return_value = None  # Do nothing when this is called
    mocker.patch("requests.post", return_value=mock_response)

    # The state needs a SQL query to work with
    state = GraphState(sql_query="SELECT COUNT(*) FROM students;")

    result = execute_sql_node(state)

    # The result should be a markdown table string
    assert "count" in result["query_result"]
    assert "100" in result["query_result"]
    print("Execute SQL user approval path test passed.")


def test_execute_sql_node_user_denies(mocker):
    """
    Tests the execution node when the user cancels the operation.
    """
    print("\n--- Testing Node: execute_sql (User Denial path) ---")
    # Mock the user input to simulate them typing 'n'
    mocker.patch("builtins.input", return_value="n")

    # Mock requests.post just in case, but it should NOT be called
    mock_post = mocker.patch("requests.post")

    state = GraphState(sql_query="SELECT 1;")
    result = execute_sql_node(state)

    assert result == {"explanation": "Query execution cancelled by user."}
    # Critically, assert that the API call was never made
    mock_post.assert_not_called()
    print("Execute SQL user denial path test passed.")
