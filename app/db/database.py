# app/db/database.py
import duckdb

# Create a connection to the database
conn = duckdb.connect('app.db')

def init_db():
    """Initialize the database and create the tables"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            date INTEGER,
            status VARCHAR,
            amount FLOAT,
            bank_activity_status VARCHAR,
            expense_description VARCHAR
        );
    """)
    conn.commit()

def insert_csv_data(csv_path:str):
    """Import data from the CSV into the database"""
    query = f"COPY statements FROM '{csv_path}' WITH HEADER = TRUE DELIMITER = ','"
    conn.execute(query)
    conn.commit()

# It's a good practice to close the connection when it's no longer needed.
# However, you can keep it open as long as your application is running.
# conn.close()
