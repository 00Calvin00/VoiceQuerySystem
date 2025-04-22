from sqlalchemy import create_engine, MetaData, text

engine = create_engine("sqlite:///database/Chinook_Sqlite.sqlite")
metadata_obj = MetaData()

def execute_sql_query(query):
    try:
        with engine.connect() as con:
            result = con.execute(text(query))
            rows = result.fetchall()
            
            # Convert SQLAlchemy row objects to dictionaries safely
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]
    except Exception as e:
        print(f"❌ SQL Execution Failed: {e}")
        return []
