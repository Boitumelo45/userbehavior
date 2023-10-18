import os
import math
import json
import requests
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import Optional

# create categories
from .create_categories import (
    remove_date_from_description, 
    group_by_date_period,
    group_by_first_word,
    generate_categories,
    transform_date,
    process_statement,
    total_daily_expenses
    ) 

# schemas
from app.schemas.categories import Frequency

# compute
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

# data processing (machine learning -predictive modeling optional)
from .data_loader import get_features_and_target

analytics_router = APIRouter()


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


@analytics_router.get('/group_transactions_by_date')
async def group_transactions():
    data = await read_statement()
    
    data = data['data'][1:-1] # remove opening statement and closing statement bank activity status

    grouped_data = defaultdict(list)

    for item in data:
        date = item.pop('DATE (YYYY/MM/DD)', None)  # Remove the date key and retrieve its value

        expense_desc = item.get('EXPENSE DESCRIPTION', None)
        if expense_desc:
            item['EXPENSE DESCRIPTION'] = expense_desc.lower()

        if date:  # Just to ensure there's a date
            grouped_data[date].append(item)
    
    grouped_data = remove_date_from_description(data_dict=grouped_data)

    return grouped_data


@analytics_router.get('/category_expenses')
async def expenses_per_category(timeframe: Frequency = Depends()):
    """Return expenses per category
    1. daily
    2. weekly
    3. monthly
    """
    data = await group_transactions()

    if timeframe.timeframe == 'daily':
        result = {}
        for _date, _data in data.items():
            grouped_data = group_by_first_word(data={_date: _data})
            result[_date] = grouped_data
        return result

    elif timeframe.timeframe == 'weekly':
        weekly_data = group_by_date_period(data, "weekly")
        result = {}
        for _date, _data in weekly_data.items():
            grouped_data = group_by_first_word(data={_date: _data})
            result[_date] = grouped_data
        return result

    elif timeframe.timeframe == 'monthly':
        monthly_data = group_by_date_period(data, "monthly")
        result = {}
        for _date, _data in monthly_data.items():
            grouped_data = group_by_first_word(data={_date: _data})
            result[_date] = grouped_data
        return result


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