import uvicorn
from fastapi import FastAPI, APIRouter
import requests
import sys
import json 
import boto3
import zlib
import logging
from datetime import datetime, timedelta
import pytz

sys.path.insert(0, '/config/')

from config.config import settings

post_router = APIRouter(prefix="/post")

# Initialize DynamoDB client with explicit credentials
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION
)


GITHUB_USERNAME = settings.GITHUB_USERNAME
ACCESS_TOKEN = settings.GITHUB_ACCESS_TOKEN

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
    data = post_commits(owner, repo)
    add_item(owner + "-" + repo, "commits", data)
    data = post_issues(owner, repo)
    add_item(owner + "-" + repo, "issues", data)
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

@post_router.get("/postcommits/{owner}/{repo}")
def post_commits(owner: str, repo: str):
    final_data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {
            "per_page": "100",
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        data_size = len(data)
        date_time_str= data[-1]['commit']['author']['date']
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
                if(check_date_time_str_within_x_days(item['commit']['author']['date'])):
                    outerIndex = index
                    break
            final_data.extend(data[0:data_size-outerIndex])
            break
    return final_data


@post_router.get("/postissues/{owner}/{repo}")
def post_issues(owner: str, repo: str):
    final_data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
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

    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {
            "per_page": "100",
            "page": page,
            "state": "closed"
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