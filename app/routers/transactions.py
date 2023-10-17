import re
import requests
from pydantic import BaseModel
from typing import Union
from difflib import SequenceMatcher
from typing_extensions import Literal
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from collections import defaultdict


app = FastAPI()

class Frequency(BaseModel):
    timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily'


@app.get("/fetch-data/")
async def fetch_data():
    # The endpoint in our FastAPI app that fetches data from the other server
    # Define the URL of the other server
    url = "http://localhost:8000/data"

    # Use requests to make a GET request to the other server
    response = requests.get(url)
    
    # Return the data fetched from the other server (assuming it returns JSON)
    return response.json()



def remove_date_from_description(data_dict: defaultdict) -> defaultdict:
    # Regular expression pattern to match dates like " 29 JUL" at the end of the string
    pattern = r'\s+\d{1,2}\s+[A-Z]{3}$'
    
    for date, transactions in data_dict.items():
        for item in transactions:
            desc = item.get('EXPENSE DESCRIPTION', "")
            if desc:
                # Replacing the matched pattern with an empty string
                new_desc = re.sub(pattern, '', desc)
                item['EXPENSE DESCRIPTION'] = new_desc

    return data_dict


def similar(a, b):
    """Return the similarity ratio of two strings."""
    return SequenceMatcher(None, a, b).ratio()


def generate_categories(transactions_data):
    # Tokenize descriptions
    tokens = []
    all_transactions = [item for sublist in transactions_data.values() for item in sublist]
    for transaction in all_transactions:
        desc = transaction.get('EXPENSE DESCRIPTION', '')
        if desc:  
            tokens.extend(re.findall(r'\b\w+\b', desc))

    # Make tokens unique and sort them
    tokens = sorted(list(set(tokens)))

    categories = defaultdict(list)

    # Check for similarity among tokens
    for i in range(len(tokens)):
        matched = False
        for category, token_list in categories.items():
            # If token matches any token in the category with 70% similarity, add to that category
            if any(similar(tokens[i], t) >= 0.4 for t in token_list):
                categories[category].append(tokens[i])
                matched = True
                break
        
        # If no match found, create a new category with the token
        if not matched:
            categories[tokens[i]].append(tokens[i])

    # Convert to regular dict for display
    return dict(categories)


def group_by_first_word(data: Union[defaultdict, list]):
    grouped_by_word = defaultdict(list)

    for transactions in data.values():
        for transaction in transactions:
            description = transaction.get("EXPENSE DESCRIPTION", "")
            
            # Check if the description is not a string or is a single character
            if not isinstance(description, str):
                if len(str(description)) <= 1:
                    first_word = transaction.get("BANK ACTIVITY STATUS", "")
                elif len(str(description)) > 1:
                    first_word = description.split()[1:]
            else:
                words = description.split()
                if len(words) > 1 and words[0].isdigit():
                    if words[1][0].isdigit():
                        first_word = words[0] # check if 0636974075 11h56 -> 0636974075
                    else:
                        first_word = " ".join(words[1:])
                else:
                    first_word = description.split()[0]

            grouped_by_word[first_word].append(transaction)

    # Further grouping or filtering by similarity (if needed)
    final_groups = defaultdict(list)
    for key in grouped_by_word:
        for other_key in grouped_by_word:
            if key != other_key and similar(key, other_key) > 0.8:  # e.g., a similarity threshold of 80%
                # Combine the groups under one key (we take the one with the highest length)
                combined_key = key if len(key) > len(other_key) else other_key
                final_groups[combined_key].extend(grouped_by_word[key])
                final_groups[combined_key].extend(grouped_by_word[other_key])
                break
        else:
            # If no similar group was found, just use the original grouping
            final_groups[key].extend(grouped_by_word[key])

    return dict(final_groups)


@app.get('/group_transactions_by_date')
async def group_transactions():
    data = await fetch_data() # get data
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


def group_by_date_period(data: defaultdict, period: str = "daily") -> defaultdict:
    """Group transactions data by the specified date period."""
    if period not in ["daily", "weekly", "monthly"]:
        raise ValueError("Invalid period")

    result = defaultdict(list)

    for date_str, transactions in data.items():
        date_obj = datetime.strptime(date_str, "%Y/%m/%d")

        if period == "weekly":
            # Use the start of the week (Monday) as the date key
            start_of_week = date_obj - timedelta(days=date_obj.weekday())
            date_key = start_of_week.strftime("%Y/%m/%d")
        elif period == "monthly":
            # Use the start of the month as the date key
            date_key = date_obj.strftime("%Y/%m/01")
        else:  # daily
            date_key = date_str
        
        result[date_key].extend(transactions)

    return result


@app.get('/categorical_by')
async def categorical_by(timeframe: Frequency = Depends()):
    """Category by frequency:
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
