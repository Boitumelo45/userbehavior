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

## References

[1] https://streamlit.io/
[2] https://plotly.com/python/plotly-express/
[3] https://pytorch.org/
[4] https://vaex.io/docs/index.html
[5] https://pypi.org/project/apache-airflow/#description
