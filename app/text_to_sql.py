import os
import re
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel, tool
from sqlalchemy import Table, Column, String, Integer, Float, insert, inspect, text
from sqlalchemy import text
from app.database_executer import engine, metadata_obj 

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

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
        "You are an AI assistant that translates natural language questions into SQL queries. "
        "You are working with the Chinook SQLite database. Here are the tables and relationships:\n\n"
        "Tables and Columns:\n"
        "- Artist(ArtistId, Name)\n"
        "- Album(AlbumId, Title, ArtistId)\n"
        "- Track(TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)\n"
        "- MediaType(MediaTypeId, Name)\n"
        "- Genre(GenreId, Name)\n"
        "- Playlist(PlaylistId, Name)\n"
        "- PlaylistTrack(PlaylistId, TrackId)\n"
        "- Customer(CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId)\n"
        "- Employee(EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email)\n"
        "- Invoice(InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total)\n"
        "- InvoiceLine(InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)\n\n"
        "Relationships:\n"
        "- Artist → Album (ArtistId)\n"
        "- Album → Track (AlbumId)\n"
        "- Track → InvoiceLine (TrackId)\n"
        "- Invoice → InvoiceLine (InvoiceId)\n"
        "- Customer → Invoice (CustomerId)\n"
        "- Employee → Customer (SupportRepId)\n"
        "- Employee (ReportsTo → EmployeeId)\n"
        "- Playlist → PlaylistTrack → Track\n\n"
        "Here is an example SQL query that correctly answers the question 'Who is the artist with the most tracks sold (by quantity)?':\n"
        "```sql\n"
        "SELECT ar.Name, SUM(il.Quantity) AS total_quantity\n"
        "FROM InvoiceLine il\n"
        "JOIN Track t ON il.TrackId = t.TrackId\n"
        "JOIN Album al ON t.AlbumId = al.AlbumId\n"
        "JOIN Artist ar ON al.ArtistId = ar.ArtistId\n"
        "GROUP BY ar.Name\n"
        "ORDER BY total_quantity DESC\n"
        "LIMIT 1;\n"
        "```\n"
        "Return only the final SQL query. Do not execute it. Do not print anything else.\n"
        "**Wrap the SQL query in a markdown block like this:**\n"
        "```sql\nSELECT ...\n```"
        "If the question doesn't seem related to the database then return an empty select immediately.\n"
        f"\n\nNatural language question: {natural_language_question}"
    )

    try:
        result = agent.run(prompt)
        print("Full agent output:\n", result)

        # 1. Check for clearly empty SELECT (bad output or irrelevant query)
        if (
            re.search(r"```sql\s*SELECT\s*(?:$|\n|```)", result.strip(), re.IGNORECASE | re.DOTALL)
            or re.match(r"^\s*SELECT\s*$", result.strip(), re.IGNORECASE)
        ):
            return "Sorry, I couldn't generate a valid SQL query for that question. Please try a different question related to music, tracks, or customers in the database."

        # 2. Try to extract SQL from a proper markdown code block
        match = re.search(r"```(?:sql)?\s*(SELECT .*?)```", result, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback: try to find any SELECT query
        alt_match = re.search(r"(SELECT[\s\S]+?)(?:;|$)", result, re.IGNORECASE)
        if alt_match:
            return alt_match.group(1).strip()

        # Fallback: if it contains SELECT and doesn't look like an error
        if "SELECT" in result.upper() and "ERROR" not in result.upper():
            return result.strip()

        # Fallback: catch text answers or irrelevant hallucinations
        if "ERROR" in result.upper() or "FINAL_ANSWER" in result.lower() or not re.search(r"SELECT\s", result, re.IGNORECASE):
            return "Sorry, I couldn't generate a valid SQL query for that question. Please try a different question related to music, tracks, or customers in the database."

        return "ERROR: Could not find SQL in model output."
    except Exception as e:
        print("❌ Text-to-SQL generation failed:", e)
        return "ERROR: SQL generation failed."
