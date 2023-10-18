# User Behavior

## How to run the project

```bash
Project structure:
.
├── README.md
├── app
│   ├── __init__.py
│   ├── api
│   ├── core
│   ├── crud
│   ├── db
│   ├── main.py
│   ├── models
│   ├── schemas
│   ├── static
│   ├── templates
│   └── test_main.py
├── app.db
├── behavior
│   ├── config.py
│   └── main.py
├── data
│   ├── images
│   └── statement.csv
├── docker
│   └── Dockerfile
├── docker-compose.yaml
├── logging.conf
├── requirements.txt
└── venv
```

# Create a predictive model

```bash
├── app/
├── analytics
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── train.py
│   ├── predict.py
│   └── model.pkl
```


###  [1] create a virtual environment
```bash
python3 -m venv venv
```

### [2] create global environment variable

```bash
touch .env
```
this file contains variables to be used in the project

```TEXT
DAILY_EXPENSES=daily_expenses
WEEKLY_EXPENSES=weekly_expenses
MONTHLY_EXPENSES=monthly_expenses
CATEGORY_EXPENSES=category_expenses
PREDICTIVE_EXPENSES=predictive_model
USER_BEHAVIOR_URL=http://127.0.0.1:8000
```

### [3] Docker container to run the project

docker-compose.yaml

```docker-compose
version: '3'

services:
  user-behavior:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:5001"
    volumes:
      - ./data:/app/data  # Adjust the paths as necessary
    networks:
      - stackcards

networks:
  stackcards:
    driver: bridge
```

Docker/Dockerfile

```docker
FROM python:3.9.0-slim

WORKDIR /UserBehavior

# Copy application code and data
COPY app app
COPY data data
COPY requirements.txt logging.conf ./

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install system dependencies
RUN apt-get update && \
    apt-get -y install postgresql && \
    apt-get clean

EXPOSE 5001

# Start Gunicorn server with Uvicorn worker
CMD ["gunicorn", "app.main:router", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5001"]
```

### [4] How to run the project locally

Run the project using docker

```bash
docker-compose up --build
```


# Guideline
Given a user's expenses statement under data/statement.csv create a program that will analyse the user's behavior. 

```TEXT
CATEGORIES
PLACES
PAYMENT
DEBITS
```

Example

Top Categories          |    % of total spend
------------------------|----------------------
Uncategorised           |
-R9 405.24              |          66.23
Insurance               |
-R3 351.00              |          23.
Transfers               |              
-R1 000.00              |           7.04
Bank Charges & Fees     |
-R445.50                |           3.14

Data analysis from the statement should be reported back to the user

Example


Needs                      |             | Wants                |             | Uncategorised  |                |
---------------------------|-------------|----------------------|-------------|----------------|----------------|
Description                | Amount (R)  | Description          | Amount (R)  | Description    |  Amount (R)    |
Insurance                  | 3 351       | Donations            |   0         | Kagiso         |  1 000         |
Loans and account          | 1 920.00    | Entertainment        |   0         | Mamikie        |  400           |
Transfers                  | 1 000.00    | Family and Friends   |   0         |
Fees and Interests         | 445.00      | Food and Drink       |   0         |
Clothing and Accessories   | 0           | Holiday and Travel   |   0         |
Education                  | 0           | Home                 |   0         |
Family and   Friends       | 0           | Medical and wellness |             |
Groceries                  | 0           |                      |             |
Home                       | 0           |                      |             |
Medical and Wellness       | 0           |                      |             |
Pets                       | 0           |                      |             |
Salaries &   wages Paid    | 0           |                      |             |
Tax                        | 0           |                      |             |
Vehicle and Transportation | 0           |                      |             |


[1] Compute total money in
[2] Compute total money out
[3] Compute variance
[4] Compute total number of transactions

# ETL - apache-airflow

Using Apache Airflow with FastAPI to load a CSV file into a DuckDB database:

```bash
├── app
│   ├── api
│   │   ├── v1
│   │   │   └── routers
│   │   │       └── airflow_trigger.py  # This file contains the FastAPI endpoint to trigger the 
├── airflow_dags
│   ├── dags
│   │   └── load_csv_to_duckdb.py
```

1. **Setup Apache Airflow**:
   - If you haven't already, install Apache Airflow and initialize its database.
   - Start the web server and scheduler.

2. **Define a Custom Airflow Operator for Loading Data**:
   - Create a custom operator (or use PythonOperator) that:
     - Reads the CSV file.
     - Loads the CSV data into the DuckDB database.
   - This custom operator can use Python's standard libraries or other libraries like `pandas` for reading CSV and interfacing with DuckDB.

3. **Create an Airflow DAG**:
   - Define a DAG in Airflow that uses the custom operator.
   - Schedule the DAG to run at your desired frequency.

4. **Integrate FastAPI with Airflow**:
   - In FastAPI, you can create an endpoint that triggers the Airflow DAG using Airflow's REST API or CLI.
   - This way, you can initiate the CSV loading process via an API call to your FastAPI service.

Here's a basic outline of what the integration might look like:

**Airflow - Load CSV to DuckDB Operator**:
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import duckdb
import pandas as pd

class LoadCSVToDuckDBOperator(BaseOperator):

    @apply_defaults
    def __init__(self, csv_path, db_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_path = csv_path
        self.db_path = db_path

    def execute(self, context):
        data = pd.read_csv(self.csv_path)
        
        con = duckdb.connect(self.db_path)
        con.register('df', data)
        con.execute("CREATE TABLE my_table AS SELECT * FROM df")
        con.close()
```

**FastAPI Endpoint to Trigger Airflow DAG**:
```python
from fastapi import FastAPI
import requests

app = FastAPI()

AIRFLOW_API_ENDPOINT = "http://AIRFLOW_HOST:PORT/api/v1/dags/YOUR_DAG_ID/dagRuns"

@app.post("/load_csv_to_duckdb/")
def load_csv_to_duckdb():
    # Trigger the Airflow DAG (assuming you've set up authentication for Airflow's REST API)
    response = requests.post(AIRFLOW_API_ENDPOINT, json={"conf":{}})
    return {"status": response.status_code, "message": response.text}
```

This is a simplified example to get you started. In practice, you'll need to handle various details like error checking, logging, Airflow authentication, handling database schema changes, and more.

Remember to adjust configurations and paths as per your actual environment.

## References

[1] https://streamlit.io/
[2] https://plotly.com/python/plotly-express/
[3] https://pytorch.org/
[4] https://vaex.io/docs/index.html
[5] https://pypi.org/project/apache-airflow/#description
