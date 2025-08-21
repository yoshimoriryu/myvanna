import asyncio
import websockets
import sys


async def listen_to_socket(websocket):
    """Waits for messages from the server and prints them."""
    try:
        while True:
            message = await websocket.recv()
            print(f"\n< Server: {message}")
    except websockets.ConnectionClosed:
        print("< Connection closed by server.")


async def send_to_socket(websocket):
    """Takes user input and sends it to the server."""
    try:
        while True:
            message = await asyncio.to_thread(input, "> You: ")
            if message.lower() in ["exit", "quit"]:
                break
            await websocket.send(message)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("< Closing connection.")


async def main(session_id):
    """The main function to connect and run the chat client."""
    uri = f"ws://localhost:8001/ws/chat/{session_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"--- Connected to WebSocket at {uri} ---")

            # Run listener and sender tasks concurrently
            listener_task = asyncio.create_task(listen_to_socket(websocket))
            sender_task = asyncio.create_task(send_to_socket(websocket))

            # Wait for the sender task to complete (e.g., user types 'exit')
            await sender_task
            listener_task.cancel()  # Clean up the listener task

    except websockets.ConnectionClosed as e:
        print(f"ERROR: Connection failed: {e.reason} (Code: {e.code})")
    except ConnectionRefusedError:
        print("ERROR: Connection refused. Is the API server running?")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_websocket.py <session_id>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
