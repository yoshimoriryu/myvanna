from sqlalchemy import create_engine, Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
import uuid

# --- Database Model Definitions ---
# Using SQLAlchemy's ORM to map Python classes to database tables.

Base = declarative_base()

class Conversation(Base):
    """
    Represents a single conversation session.
    A session can contain multiple messages.
    """
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This creates the relationship, allowing us to access conversation.messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """
    Represents a single message within a conversation.
    """
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    
    # The 'type' could be 'human', 'ai', 'system', etc.
    # This matches the 'type' attribute in LangChain's BaseMessage objects.
    message_type = Column(String, nullable=False) 
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This links the message back to its parent conversation
    conversation = relationship("Conversation", back_populates="messages")


# --- Database Connection and Session Management ---
# This section will be used by the API to connect to the database.

# We will initialize these in the main API file after loading the config
engine = None
SessionLocal = None

def init_database_connection(db_url: str):
    """
    Initializes the database engine and session maker.
    This should be called once during the application's startup.
    """
    global engine, SessionLocal
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """
    Creates all the tables defined in the Base metadata.
    """
    if engine:
        Base.metadata.create_all(bind=engine)
    else:
        raise RuntimeError("Database engine not initialized. Call init_database_connection first.")