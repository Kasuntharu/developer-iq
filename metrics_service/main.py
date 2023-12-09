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
app = FastAPI()


# Initialize DynamoDB client with explicit credentials
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='AKIAWWJOX62Z4QMOXE6S',
    aws_secret_access_key='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',
    region_name='us-east-1'
)


GITHUB_USERNAME = "Kasuntharu"
ACCESS_TOKEN = "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" #remove zzz

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
    url = f"https://api.github.com/repos/facebook/react-native/pulls"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # return response.json()
    add_item("asd2",1,response.json())
    

def add_item(p_key: str, sort_key: int, data: dict ):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id='AKIAWWJOX62Z4QMOXE6S',
        aws_secret_access_key='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',
        region_name='ap-southeast-1'
    )

    for table in dynamodb.tables.all():
        print(f"Table: {table.name}")

    table = dynamodb.Table('dev-metrics')
    
    response = table.put_item(
        Item={
            'user_name': p_key,
            'id': sort_key,
            'data': {'data': data}
        }
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Item added successfully!")
        return "done"
    else:
        print("Error adding item.")
        return "failed"



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










