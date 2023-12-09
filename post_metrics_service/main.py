from typing import Union , Optional
from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException  # Importing HTTPException
import uvicorn
from fastapi import FastAPI, APIRouter
import requests
from pydantic import BaseModel
import json 
import boto3
import zlib
import logging
from datetime import datetime, timedelta
import pytz

post_router = APIRouter(prefix="/post")

# Initialize DynamoDB client with explicit credentials
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='AKIAWWJOX62Z4QMOXE6S',
    aws_secret_access_key='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',
    region_name='ap-southeast-1'
)


GITHUB_USERNAME = "Kasuntharu"
ACCESS_TOKEN = "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"

BASE_URL = "https://api.github.com"

headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

table_name = 'dev-iq-metrics'

@post_router.get("/")
def read_root():
    return {"Hello": "World"}

@post_router.get("/init/{owner}/{repo}")
def test(owner: str, repo: str):
    data = post_pull_requests(owner, repo)
    add_item(owner + "-" + repo, "pulls", data)
    return data

@post_router.get("/postpulls/{owner}/{repo}")
def post_pull_requests(owner: str, repo: str):
    final_data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "per_page": "100",
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        data_size = len(data)
        date_time_str= data[-1]['created_at']
        given_date_time = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
        # Get the current datetime in UTC
        current_time = datetime.now(pytz.utc)
        # Compute the difference
        time_difference = current_time - given_date_time
        # Check if the difference is less than or equal to 30 days
        if abs(time_difference) <= timedelta(days=30):
            # print("The given date-time is within 30 days from now.")
            # increment page and continue
            final_data.extend(data)
            page+=1
            continue
        else:
            # print("The given date-time is not within 30 days from now.")
            # same page upper elements
            outerIndex = 0
            for index, item in enumerate(reversed(data)):
                if(check_date_time_str_within_x_days(item['created_at'])):
                    outerIndex = index
                    break
            final_data.extend(data[0:data_size-outerIndex])
            break
    return final_data


def check_date_time_str_within_x_days(date_time_str: str, limit = 30):
    given_date_time = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
        # Get the current datetime in UTC
    current_time = datetime.now(pytz.utc)
    # Compute the difference
    time_difference = current_time - given_date_time
    # Check if the difference is less than or equal to 30 days
    if abs(time_difference) <= timedelta(days=limit):
        # print("within 30 days")
        return True
    else:
        # print("not within 30 days")
        return False





def add_item(p_key: str, type: str, data: dict ):
    for table in dynamodb.tables.all():
        print(f"Table: {table.name}")

    table = dynamodb.Table(table_name)
    
    response = table.put_item(
        Item={
            'id': p_key,
            'type': type,
            'data': compress_data(data)
        }
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Item added successfully!")
        return "done"
    else:
        print("Error adding item.")
        return "failed"

def compress_data(data):
        try:
            serialized_data = json.dumps(data).encode()
            return zlib.compress(serialized_data)
        except Exception as e:
            logging.error(f"Error compressing data: {e}")
            return None

app = FastAPI()
app.include_router(post_router)