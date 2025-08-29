import asyncio
import uvicorn
import uuid
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage
import logging

# --- Updated Imports for New Structure ---
from src.chatbot.agent import build_graph, initialize_llm_and_vanna, GraphState
from src.chatbot import state_db
from src.chatbot.state_db import Message, Conversation
from src.vanna_engine import config

# --- API Setup ---
app = FastAPI(
    title="MyVanna Multi-Agent Chatbot API",
    description="An API for interacting with the secure, multi-agent Vanna chatbot.",
    version="1.0.0",
)


# --- Pydantic Models ---
class ChatRequest(BaseModel):
    session_id: str | None = Field(
        None, description="A unique identifier for the conversation session."
    )
    message: str = Field(..., description="The user's message.")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    error: bool = False
    error_message: str | None = None
    generated_sql: str | None = None


# --- Global Agent Variable ---
agent_app = None


# --- Database Dependency ---
def get_db():
    db = state_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Application Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    print("--- API Starting Up ---")
    global agent_app
    print("Connecting to the chatbot state database...")
    db_url = (
        f"postgresql+psycopg2://{config.CHATBOT_DB_USER}:{config.CHATBOT_DB_PASSWORD}@"
        f"{config.CHATBOT_DB_HOST}:5432/{config.CHATBOT_DB_NAME}"
    )
    # logging.INFO(db_url)
    state_db.init_database_connection(db_url)
    state_db.create_tables()
    print("Database connection successful.")
    print("Initializing Vanna domains and building the agent...")
    agent_app = build_graph()
    initialize_llm_and_vanna()
    print("--- API Ready ---")


# --- Helper Functions ---
def convert_db_messages_to_langchain(messages: List[Message]) -> List[BaseMessage]:
    return [HumanMessage(content=msg.content) for msg in messages if msg.message_type == "human"]


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    Handles a persistent chat session over WebSockets.
    """
    await websocket.accept()

    # First, verify that the conversation session exists
    conversation = db.query(Conversation).filter(Conversation.id == session_id).first()
    if not conversation:
        await websocket.send_json(
            {"error": True, "message": f"Session ID '{session_id}' not found."}
        )
        await websocket.close()
        return

    await websocket.send_json({"error": False, "message": "Connection successful. Ready to chat."})

    try:
        while True:
            # Wait for a message from the client
            user_message_content = await websocket.receive_text()

            # --- This logic is nearly identical to the HTTP endpoint ---
            # 1. Save the user's message to the database
            user_message = Message(
                conversation_id=session_id, message_type="human", content=user_message_content
            )
            db.add(user_message)
            db.commit()

            # 2. Load history and invoke the agent
            history_from_db = conversation.messages
            langchain_history = convert_db_messages_to_langchain(history_from_db)
            initial_state: GraphState = {"messages": langchain_history}

            import builtins

            original_input = builtins.input
            builtins.input = lambda _: "y"  # Auto-approve SQL
            try:
                final_state = agent_app.invoke(initial_state)
                response_data = (
                    final_state.get("error_message")
                    or final_state.get("explanation")
                    or "An unexpected issue occurred."
                )
                is_error = "error_message" in final_state

                sql_to_return = None
                if not is_error and response_data:
                    ai_message = Message(
                        conversation_id=session_id, message_type="model", content=response_data
                    )
                    db.add(ai_message)
                    db.commit()

                    if config.IS_DEV:
                        sql_to_return = final_state.get("sql_query")

                # 3. Send the response back over the WebSocket
                await websocket.send_json(
                    {
                        "session_id": session_id,
                        "response": response_data,
                        "error": is_error,
                        "error_message": final_state.get("error_message"),
                        "generated_sql": sql_to_return,
                    }
                )
            finally:
                builtins.input = original_input

    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
    except Exception as e:
        print(f"An error occurred in WebSocket session {session_id}: {e}")
        await websocket.send_json({"error": True, "message": "An internal error occurred."})
    finally:
        db.close()


# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    if not agent_app:
        raise HTTPException(status_code=503, detail="Chatbot agent is not available.")

    session_id = request.session_id
    if session_id:
        conversation = db.query(Conversation).filter(Conversation.id == session_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")
    else:
        conversation = Conversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        session_id = conversation.id

    user_message = Message(
        conversation_id=session_id, message_type="human", content=request.message
    )
    db.add(user_message)
    db.commit()

    history_from_db = conversation.messages
    langchain_history = convert_db_messages_to_langchain(history_from_db)

    initial_state: GraphState = {"messages": langchain_history}

    import builtins

    original_input = builtins.input
    builtins.input = lambda _: "y"
    try:
        final_state = agent_app.invoke(initial_state)

        sql_to_return = None
        if config.IS_DEV:
            sql_to_return = final_state.get("sql_query")

        response_data = (
            final_state.get("error_message")
            or final_state.get("explanation")
            or "An unexpected issue occurred."
        )
        is_error = "error_message" in final_state

        if not is_error and response_data:
            ai_message = Message(
                conversation_id=session_id, message_type="model", content=response_data
            )
            db.add(ai_message)
            db.commit()

        return ChatResponse(
            session_id=session_id,
            response=response_data,
            error=is_error,
            error_message=final_state.get("error_message"),
            generated_sql=sql_to_return,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
    finally:
        builtins.input = original_input


@app.get("/history/{session_id}", response_model=List[Dict[str, Any]])
async def get_conversation_history(session_id: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == session_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Session ID not found.")
    return [
        {"type": msg.message_type, "content": msg.content, "created_at": msg.created_at}
        for msg in conversation.messages
    ]


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="The ID of the AI message being rated.")
    rating: int = Field(
        ..., description="The feedback rating (e.g., 1 for thumbs up, -1 for thumbs down)."
    )
    text: str | None = Field(None, description="Optional textual feedback from the user.")


@app.post("/feedback")
async def receive_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Receives and stores user feedback for a specific AI message.
    """
    message_to_update = db.query(Message).filter(Message.id == request.message_id).first()

    if not message_to_update:
        raise HTTPException(status_code=404, detail="Message ID not found.")

    if message_to_update.message_type != "model":
        raise HTTPException(
            status_code=400, detail="Feedback can only be provided for AI messages."
        )

    message_to_update.feedback_rating = request.rating
    message_to_update.feedback_text = request.text
    db.commit()

    return {"status": "success", "message": "Feedback received successfully."}


# poetry run uvicorn run_api:app --reload --port 8001 --host 0.0.0.0
