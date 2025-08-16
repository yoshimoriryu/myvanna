import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine, text

# --- Add 'src' to path to import config ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(project_root, 'src'))
from vanna_engine import config
# ---

app = FastAPI()

class SQLQuery(BaseModel):
    sql: str

# Create the database engine once when the API starts
try:
    db_url = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
    engine = create_engine(db_url)
    print("--- Secure API connected to PostgreSQL successfully. ---")
except Exception as e:
    print(f"FATAL ERROR: Could not connect to database: {e}")
    engine = None

@app.post("/execute-sql")
def execute_sql(query: SQLQuery):
    if engine is None:
        raise HTTPException(status_code=500, detail="Database connection is not available.")
    
    print(f"--- Received SQL for execution: ---\n{query.sql}\n---------------------------------")
    
    # SECURITY: Simple check to prevent obviously harmful queries.
    # You can build much more robust rules here.
    disallowed_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "GRANT", "REVOKE"]
    if any(keyword in query.sql.upper() for keyword in disallowed_keywords):
        raise HTTPException(status_code=403, detail="Execution of this query type is forbidden.")

    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(query.sql), connection)
        # Convert to JSON for the API response
        return df.to_dict(orient='records')
    except Exception as e:
        # Return a proper error message to the chatbot
        raise HTTPException(status_code=400, detail=f"Error executing SQL: {str(e)}")
