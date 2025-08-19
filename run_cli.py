from langchain_core.messages import HumanMessage
import sys

# --- Updated Imports for New Structure ---
# Add the project root to the path to allow for absolute imports
sys.path.insert(0, ".")
from src.chatbot.agent import (
    initialize_llm_and_vanna,
    build_graph,
    AVAILABLE_DOMAINS,
)


def main_cli_loop():
    """
    The main application loop for the command-line chatbot.
    """
    # Initialize everything once at the start
    print("--- Initializing Chatbot for CLI ---")
    available_domains = initialize_llm_and_vanna()
    if not available_domains:
        print("\nCould not find any Vanna domains. Please run the trainer first. Exiting.")
        return

    app = build_graph()

    print(f"\n--- Starting Chat ---")
    print("I can answer questions about the following domains:", available_domains)
    print("Type 'exit' or 'quit' to end the conversation.")

    # This will hold our full conversation history for the CLI session
    messages = []

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            messages.append(HumanMessage(content=user_input))
            initial_state = {"messages": messages}

            # Invoke the LangGraph agent
            final_state = app.invoke(initial_state)

            # --- Display the result to the user ---
            if final_state.get("error_message"):
                print(f"\nAI (Error): {final_state['error_message']}")
                # Remove the last message from history if it caused an error
                messages.pop()
            elif final_state.get("explanation"):
                print(f"\nAI: {final_state['explanation']}")
            else:
                print("\nAI: I'm sorry, an unexpected issue occurred.")

        except (KeyboardInterrupt, EOFError):
            break

    print("\n--- Conversation Ended ---")


if __name__ == "__main__":
    # To run the CLI, you will now execute `python run_cli.py`
    main_cli_loop()
