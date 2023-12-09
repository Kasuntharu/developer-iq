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

get_router = APIRouter(prefix="/get")

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
    openpulls = len([singleEntry for singleEntry in data if isUser(singleEntry, user)])
    totalPulls = len(data)
    return {
        "user": user,
        "total_open_pull_requests": totalPulls,
        "user_opend_pull_requests": openpulls
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


app = FastAPI()
app.include_router(get_router)