import uvicorn
from fastapi import FastAPI, APIRouter
import requests
import json 
import boto3
import zlib
import logging
from datetime import datetime, timedelta
import pytz
import sys

sys.path.insert(0, '/config/')

from config.config import settings

get_router = APIRouter(prefix="/get")

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


@get_router.get("/")
def read_root():
    return "Hello World! Service is up and running!"

@get_router.get("/dynamodb")
def test():
    return get_item("latest", 'pulls')

@get_router.get("/getpulls/{owner}/{repo}")
def get_pull_requests(owner: str, repo: str):
    return get_item(owner + "-" + repo, 'pulls')

@get_router.get("/getpulls/{owner}/{repo}/user/{user}")
def get_user_pull_requests(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "pulls")
    return [singleEntry for singleEntry in data if isUser(singleEntry, user)]


@get_router.get("/getpulls/{owner}/{repo}/user/{user}/summary")
def get_user_pull_request_summary(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "pulls")
    open_pulls = len([singleEntry for singleEntry in data if isUser(singleEntry, user)])
    total_Pulls = len(data)
    return {
        "user": user,
        "total_open_pull_requests": total_Pulls,
        "user_opend_pull_requests": open_pulls
    }


@get_router.get("/getcommits/{owner}/{repo}")
def get_commits(owner: str, repo: str):
    return get_item(owner + "-" + repo, 'commits')

@get_router.get("/getcommits/{owner}/{repo}/user/{user}")
def get_user_commits(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "commits")
    return [singleEntry for singleEntry in data if isUser(singleEntry, user)]


@get_router.get("/getcommits/{owner}/{repo}/user/{user}/summary")
def get_user_commit_summary(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "commits")
    user_commits = len([singleEntry for singleEntry in data if isUser(singleEntry, user)])
    total_commits = len(data)
    return {
        "user": user,
        "total_repo_commits": total_commits,
        "user_commits": user_commits
    }

@get_router.get("/getcontributors/{owner}/{repo}")
def get_contributors(owner: str, repo: str):
    return get_item(owner + "-" + repo, 'contributors')


@get_router.get("/getissues/{owner}/{repo}")
def get_issues(owner: str, repo: str):
    return get_item(owner + "-" + repo, 'issues')

@get_router.get("/getissues/{owner}/{repo}/user/{user}")
def get_user_issues(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "issues")
    return [singleEntry for singleEntry in data if isUser(singleEntry, user)]


@get_router.get("/getissues/{owner}/{repo}/user/{user}/summary")
def get_user_issues_summary(owner: str, repo: str, user: str):
    data = get_item(owner + "-" + repo, "issues")
    user_issues = [singleEntry for singleEntry in data if isUser(singleEntry, user)]
    user_issues_len = len(user_issues)
    total_issues = len(data)
    user_closed_issues = [singleEntry for singleEntry in user_issues if isIssueClosed(singleEntry)]
    user_closed_issues_len = len(user_closed_issues)

    # Initialize total_time as a timedelta object
    total_time = timedelta()
    # Count the number of issues processed
    count = 0
    average_time = 0
    delta_str=""

    for issue in user_closed_issues:
        if "closed_at" in issue and "created_at" in issue:
            created_at = parse_iso_datetime(issue["created_at"])
            closed_at = parse_iso_datetime(issue["closed_at"])
            total_time += closed_at - created_at
            count += 1
    
    if count > 0:
        average_time = total_time / count
        print(f"Average time to close issue: {average_time}")
        total_seconds = int(average_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        delta_str = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    else:
        print("No issues with close times found.") 

    return {
        "user": user,
        "total_repo_issues": total_issues,
        "user_issues": user_issues_len,
        "user_closed_issues_count": user_closed_issues_len,
        "average_time_to_close_issue": str(average_time) + " (" + delta_str + ")" ,
        "user_closed_issues": user_closed_issues
    }




def get_item(p_key: str, type: str):
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'id': p_key, 'type': type })
    d = decompress_data(response['Item']['data'].value)
    return d

def decompress_data(compressed_data):
    try:
        decompressed_data = zlib.decompress(compressed_data)
        return json.loads(decompressed_data)
    except Exception as e:
        logging.error(f"Error decompressing data: {e}")
        return None

def isUser(data:dict, user: str) -> bool:
    return data.get('user', {}).get('login') == user

def isIssueClosed(data:dict) -> bool:
    return data.get('state', {}) == "closed"

# Function to parse ISO 8601 formatted datetime strings
def parse_iso_datetime(dt_str):
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

app = FastAPI()
app.include_router(get_router)