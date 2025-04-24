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
    "```\n\n"

    "**IMPORTANT INSTRUCTIONS**\n"
    "- If the question is not related to the database schema (e.g., no relevant tables like Artist, Album, Track, etc.), DO NOT generate SQL.\n"
    "- Instead, return this:\n"
    "```plaintext\n"
    "EXPLANATION: Your question does not mention any relevant table or column names from the Chinook database. Try asking about artists, albums, tracks, customers, invoices, or other relevant entities.\n"
    "```\n"
    "- If the question is valid, return only the SQL in a code block:\n"
    "```sql\n"
    "SELECT ...\n"
    "```\n"
    "- DO NOT print or return query results.\n"
    "- DO NOT include any other text unless it's an EXPLANATION block.\n\n"

    f"Natural language question: {natural_language_question}"
)


    try:
        result = str(agent.run(prompt)).strip()
        print("Full agent output:\n", result)

        # Explanation block
        if result.startswith("```plaintext") and "EXPLANATION:" in result:
            explanation = re.search(r"EXPLANATION:(.*)", result, re.DOTALL)
            if explanation:
                return "EXPLANATION:" + explanation.group(1).strip()
            return "EXPLANATION: The model detected your question is not related to the Chinook database schema."

        # Executed result
        if re.match(r"^\(?.*['\"].*['\"].*\)?$", result):
            return f"[EXECUTED_RESULT]{result}"

        # Extract SQL from markdown
        match = re.search(r"```(?:sql)?\s*(SELECT .*?)```", result, re.DOTALL | re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            if extracted.upper() in ["SELECT", "SELECT ''", "SELECT \"\"", "SELECT 'NONE' AS RESULT"]:
                return "EXPLANATION: The model attempted to respond, but the SQL query was empty or invalid."
            return extracted

        # Fallback extraction
        alt_match = re.search(r"(SELECT[\s\S]+?)(?:;|$)", result, re.IGNORECASE)
        if alt_match:
            return alt_match.group(1).strip()

        if "SELECT" in result.upper() and "ERROR" not in result.upper():
            return result.strip()

        return "EXPLANATION: The model could not generate a valid SQL query for this input."

    except Exception as e:
        print("❌ Text-to-SQL generation failed:", e)
        return "ERROR: SQL generation failed."
