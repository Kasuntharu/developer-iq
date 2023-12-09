from typing import Union , Optional
from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException  # Importing HTTPException

import uvicorn
from fastapi import FastAPI
import requests
from pydantic import BaseModel
import json 
import boto3

import zlib
import logging
from datetime import datetime
import pytz

app = FastAPI()


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

@app.get("/")
def read_root():
    return {"Hello": "World"}

#List Down users for a Repository 
@app.get("/repository_users/{owner}/{repo}")
def get_repository_users(owner: str, repo: str):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contributors"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository users")

        contributors = response.json()
        users = [contributor["login"] for contributor in contributors]

        return {
            "repository": f"{owner}/{repo}",
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository users: {str(e)}")





#Getting Matrices
@app.get("/repository_metrics/{owner}/{repo}/{username}")
def get_repository_metrics(owner: str, repo: str, username: str):
    url = f"{BASE_URL}/repos/{owner}/{repo}"

    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository details")

        repository = response.json()

        # Get commits for the repository
        commits_url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
        commits_response = requests.get(commits_url, headers=headers)
        commits_data = commits_response.json()
        commits = len([commit for commit in commits_data if commit['author']['login'] == username])

        # Get pull requests for the repository
        pulls_url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        pulls_response = requests.get(pulls_url, headers=headers)
        pull_requests_data = pulls_response.json()
        pull_requests = len([pr for pr in pull_requests_data if pr['user']['login'] == username])

        # Get issues for the repository
        issues_url = f"{BASE_URL}/repos/{owner}/{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers, params={"state": "closed"})
        issues_resolved_data = issues_response.json()
        issues_resolved = len([
            issue for issue in issues_resolved_data if issue['user']['login'] == username or issue['closed_by']['login'] == username
        ])

        # Get merge requests for the repository (assuming they are equivalent to pull requests)
        merge_requests = len([pr for pr in pull_requests_data if pr['user']['login'] == username])

        return {
            "repository": f"{owner}/{repo}",
            "username": username,
            "commits": commits,
            "pull_requests_created": pull_requests_created,
            "issues_resolved": issues_resolved,
            "pull_requests_merged": merge_requests_creted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")



@app.get("/repos/{owner}/{repo}/pulls")
def get_pulls(owner: str, repo: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@app.get("/repos/{owner}/{repo}/pulls/{user}")
def get_pulls_by_user(owner: str, repo: str, user: str):
    #url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return "Hello"


@app.get("/dynamodb")
def test():
    final_data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/facebook/react-native/pulls?per_page=16&page={page}"
        response = requests.get(url, headers=headers)
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
            print("The given date-time is within 30 days from now.")
            # increment page and continue
            final_data.extend(data)
            page+=1
            continue
        else:
            print("The given date-time is not within 30 days from now.")
            # same page upper elements
            outerIndex = 0
            for index, item in enumerate(reversed(data)):
                if(check_date_time_str_within_x_days(item['created_at'])):
                    outerIndex = index
                    break
            final_data.extend(data[0:data_size-outerIndex])
            break
    # return final_data
    # return len(final_data)
    add_item("asd2",final_data)
    return get_item("asd2")

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

def test_old():
    url = f"https://api.github.com/repos/facebook/react-native/pulls?per_page=100"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    add_item("asd2",response.json())
    return get_item("asd2")

def get_item(p_key: str):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id='AKIAWWJOX62Z4QMOXE6S',
        aws_secret_access_key='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',
        region_name='ap-southeast-1'
    )

    table = dynamodb.Table('dev-iq-metrics')
    response = table.get_item(Key={'id': p_key})
    d = decompress_data(response['Item']['data'].value)
    return d
    # return [dd.get('url') for dd in d if isUser(dd, 'janicduplessis')]
    # return [dd.get('url') for dd in d if isUser(dd, 'Kasuntharu')]

def add_item(p_key: str, data: dict ):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id='AKIAWWJOX62Z4QMOXE6S',
        aws_secret_access_key='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',
        region_name='ap-southeast-1'
    )

    for table in dynamodb.tables.all():
        print(f"Table: {table.name}")

    table = dynamodb.Table('dev-iq-metrics')
    
    response = table.put_item(
        Item={
            'id': p_key,
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

def decompress_data(compressed_data):
    try:
        decompressed_data = zlib.decompress(compressed_data)
        return json.loads(decompressed_data)
    except Exception as e:
        logging.error(f"Error decompressing data: {e}")
        return None


#This is the updated version. this seems right
@app.get("/repository_metricS/{owner}/{repo}/{username}")
def get_repository_metrics(owner: str, repo: str, username: str):
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    repository_info = requests.get(url, headers=headers).json()

    # Placeholder variables for metrics
    commits = 0
    pull_requests_created = 0
    issues_resolved = 0
    pull_requests_merged = 0

    # Fetch repository information
    repository_info = requests.get(url, headers=headers)
    if repository_info.status_code != 200:
        return {"error": "Repository not found or unauthorized access"}

    # Fetch commits by the specified user
    commits_url = f"{BASE_URL}/repos/{owner}/{repo}/commits?author={username}"
    commits_info = requests.get(commits_url, headers=headers).json()
    commits = len(commits_info)

    # Fetch pull requests created by the specified user
    pull_requests_url = f"{BASE_URL}/repos/{owner}/{repo}/pulls?creator={username}"
    pull_requests_info = requests.get(pull_requests_url, headers=headers).json()
    pull_requests_created = len(pull_requests_info)

    # Fetch issues resolved by the specified user (assuming issues closed by comments or code changes)
    issues_url = f"{BASE_URL}/repos/{owner}/{repo}/issues?state=closed&creator={username}"
    issues_info = requests.get(issues_url, headers=headers).json()
    issues_resolved = len(issues_info)

    # Fetch merged pull requests by the specified user
    merged_pull_requests_url = f"{BASE_URL}/repos/{owner}/{repo}/pulls?state=closed&creator={username}&base=master"
    merged_pull_requests_info = requests.get(merged_pull_requests_url, headers=headers).json()
    pull_requests_merged = len([pr for pr in merged_pull_requests_info if pr.get('merged_at')])

    # Return metrics
    return {
        "repository": f"{owner}/{repo}",
        "username": username,
        "commits": commits,
        "pull_requests_created": pull_requests_created,
        "issues_resolved": issues_resolved,
        "pull_requests_merged": pull_requests_merged
    }

def isUser(data:dict, user: str) -> bool:
    return data.get('user', {}).get('login') == user


from datetime import datetime, timedelta
import requests

@app.get("/repository_metrics_month/{owner}/{repo}/{username}")
def get_repository_metrics(owner: str, repo: str, username: str):
    try:
        headers = {
            "Authorization": f"token {ACCESS_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Placeholder variables for metrics
        commits = 0
        pull_requests_created = 0
        issues_resolved = 0
        pull_requests_merged = 0

        # Calculate 'since' parameter for the past XXX
        past_month = datetime.utcnow() - timedelta(days=30)
        since_date = past_month.isoformat()

        # Fetch commits by the specified user within the last month
        commits_url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
        params = {
            "author": username,
            "since": since_date
        }
        commits_info = requests.get(commits_url, headers=headers, params=params).json()
        commits = len(commits_info)

        # Fetch pull requests created by the specified user within the last month
        pull_requests_url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            "creator": username,
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "since": since_date
        }
        pull_requests_info = requests.get(pull_requests_url, headers=headers, params=params).json()
        pull_requests_created = len(pull_requests_info)

        # Fetch issues resolved by the specified user within the last month
        issues_url = f"{BASE_URL}/repos/{owner}/{repo}/issues"
        params = {
            "creator": username,
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "since": since_date
        }
        issues_info = requests.get(issues_url, headers=headers, params=params).json()
        issues_resolved = len(issues_info)

        # Fetch merged pull requests by the specified user within the last month
        merged_pull_requests_url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            "creator": username,
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "base": "master",
            "since": since_date
        }
        merged_pull_requests_info = requests.get(merged_pull_requests_url, headers=headers, params=params).json()
        pull_requests_merged = len([pr for pr in merged_pull_requests_info if pr.get('merged_at')])

        # Return metrics
        return {
            "repository": f"{owner}/{repo}",
            "username": username,
            "commits": commits,
            "pull_requests_created": pull_requests_created,
            "issues_resolved": issues_resolved,
            "pull_requests_merged": pull_requests_merged
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository metrics: {str(e)}")











from datetime import datetime, timedelta
import requests

@app.get("/repository_users_all/{owner}/{repo}")
def get_repository_users(owner: str, repo: str):
    try:
        contributors = []
        page = 1
        per_page = 100  # Maximum items per page
        url = f"{BASE_URL}/repos/{owner}/{repo}/contributors"

        # Calculate 'since' parameter for the past month
        past_month = datetime.utcnow() - timedelta(days=30)
        since_date = past_month.strftime("%Y-%m-%dT%H:%M:%SZ")

        while True:
            params = {
                "per_page": per_page,
                "page": page,
                "since": since_date
            }

            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository users")

            page_contributors = response.json()
            contributors.extend([contributor["login"] for contributor in page_contributors])

            if len(page_contributors) < per_page:
                break  # Reached the last page

            page += 1

        return {
            "repository": f"{owner}/{repo}",
            "users": contributors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository users: {str(e)}")














