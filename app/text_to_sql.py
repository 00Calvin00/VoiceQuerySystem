import os
import re
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel, tool
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, insert, inspect, text
from sqlalchemy import text
#from app.text_to_sql import engine 

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
engine = create_engine("sqlite:///database/test_database.db")  # You can change to memory db for testing
metadata_obj = MetaData()

# Define a sample table
receipts = Table(
    "receipts",
    metadata_obj,
    Column("receipt_id", Integer, primary_key=True),
    Column("customer_name", String(16)),
    Column("price", Float),
    Column("tip", Float),
)

metadata_obj.create_all(engine)
#TODO: Remember to take this out?? Use actual databse instead??
# Optional: Insert rows if needed
def insert_sample_data():
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM receipts"))
        count = result.scalar()

        if count == 0:
            print("📥 Inserting sample data...")
            rows = [
                {"receipt_id": 1, "customer_name": "Alan Payne", "price": 12.06, "tip": 1.20},
                {"receipt_id": 2, "customer_name": "Alex Mason", "price": 23.86, "tip": 0.24},
                {"receipt_id": 3, "customer_name": "Woodrow Wilson", "price": 53.43, "tip": 5.43},
                {"receipt_id": 4, "customer_name": "Margaret James", "price": 21.11, "tip": 1.00},
            ]
            for row in rows:
                conn.execute(insert(receipts).values(**row))
        else:
            print(f"ℹ️ Table already has {count} entries. Skipping insert.")


# Only call once if needed
insert_sample_data()

# Describe the table
inspector = inspect(engine)
columns_info = [(col["name"], col["type"]) for col in inspector.get_columns("receipts")]
table_description = "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])

@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table. The table is named 'receipts'. Description:
    {table_description}

    Args:
        query: SQL to run.
    """
    output = ""
    with engine.connect() as con:
        rows = con.execute(text(query))
        for row in rows:
            output += "\n" + str(row)
    return output

# Build the agent
agent = CodeAgent(
    tools=[sql_engine],
    model=InferenceClientModel(model_id="meta-llama/Meta-Llama-3.1-8B-Instruct", token=HF_TOKEN),
)

def generate_sql(natural_language_question: str) -> str:
    prompt = (
        "You are an AI assistant working with an SQLite database that contains the following table:\n"
        "Table: receipts\n"
        "Columns:\n"
        "- receipt_id (INTEGER)\n"
        "- customer_name (VARCHAR)\n"
        "- price (FLOAT)\n"
        "- tip (FLOAT)\n\n"
        f"Translate the following natural language question into a SQL query: \n{natural_language_question}"
    )
    try:
        result = agent.run(prompt)
        # Extract SQL query from result text
        match = re.search(r"```sql\s+(.*?)```", result, re.DOTALL | re.IGNORECASE)

        if match:
            sql_query = match.group(1).strip()
            return sql_query
        else:
            return "ERROR: Could not find SQL in model output."
    except Exception as e:
        print("❌ Text-to-SQL generation failed:", e)
        return "ERROR: SQL generation failed."

def execute_sql_query(query):
    try:
        with engine.connect() as con:
            result = con.execute(text(query))
            return [dict(row) for row in result]
    except Exception as e:
        print(f"❌ SQL Execution Failed: {e}")
        return []