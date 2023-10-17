import os
import math
import json
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Path, Query, HTTPException
from typing import Optional

# data analytics
import pandas as pd

# unittesting
from pytest import mark

# compute
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

# data processing (machine learning -predictive modeling optional)
from .data_loader import get_features_and_target


analytics_router = APIRouter()

@mark.parametrize('input_data, output_data', [(i, f"{str(i)[:4]}/{str(i)[4:6]}/{str(i)[6:]}") for i in [20230511 + j for j in range(10)]])
def test_transform_date(input_data, output_data):
    assert transform_date(input_data) == output_data


def transform_date(input_date):
    # Convert the input to string in case it's an integer
    date_str = str(input_date)
    
    # Convert string to datetime object
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    
    # Format datetime object to desired format
    formatted_date = date_obj.strftime('%Y/%m/%d')
    return formatted_date


def process_statement(statement: str=os.path.join('data', 'statement.csv')) -> pd.DataFrame:
    """Process csv and return a dataframe"""
    df = pd.read_csv(statement)
    df = df.fillna(0) # replace all NaNs with 0
    
    # get dataframe columns
    columns = list(df.columns)
    date_column = df[columns[0]].to_list()
    format_date_column = list(map(transform_date, date_column))
    df[columns[0]] = format_date_column

    return df


def total_daily_expenses(bank_statement: list) -> pd.DataFrame:
    """payload and return summed daily expenses"""
    daily_expenses = defaultdict(list)

    for item in bank_statement:
        if item['STATUS'] == 'OPEN' or item['STATUS'] == 'CLOSE':
            pass
        else:
            if item['AMOUNT'] > 0: # positive cash flow
                pass
            else:
                daily_expenses[item['DATE (YYYY/MM/DD)']].append((item['AMOUNT']))
    
    def _sum(data:dict)->dict:
        expenses = {}
        for date, amounts in data.items():
            expenses[date] = round(abs(sum(amounts)), 3)
        return expenses

    return _sum(data=daily_expenses)


@analytics_router.get('/data')
async def read_statement():
    """Read CSV file statement and return data as dataframe"""
    df = process_statement() # read a csv file and get dataframe
    res = df.to_json(orient="records")
    parsed = json.loads(res)

    return parsed


@analytics_router.get('/daily_expenses')
async def daily_expenses():
    """Return daily expenses tabulated data"""
    res = await read_statement()
    total_expenses = total_daily_expenses(res)
    
    return total_expenses


@analytics_router.get('/weekly_expenses')
async def weekly_expenses():
    """Return weekly expenses tabulated data"""
    pass


@analytics_router.get('/monthly_expenses')
async def monthly_expenses():
    """Return monthly expenses tabulated data"""
    pass


@analytics_router.get('/category_expenses')
async def expenses_per_category():
    """Return expenses per category, monthly"""
    pass


# machine learning model - optional
#X, y = get_features_and_target()
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

#model = LinearRegression()
#model.fit(X_train, y_train)

@analytics_router.post('/predictive_model')
async def predictive_behavior(features: list):
    """
    Receive a list of features, make a prediction using a trained model, 
    and return the prediction.
    """
    try:
        features_array = np.array(features).reshape(1, -1)
        prediction = model.predict(features_array)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))