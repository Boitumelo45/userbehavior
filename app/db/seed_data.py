import os
from .database import init_db, insert_csv_data


def seed():
    """Initialize the database and import the CSV data"""
    init_db()
    insert_csv_data(os.path.join('data', 'statement.csv'))


# Run the seed function
if __name__ == "__main__":
    seed()
