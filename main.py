from fastapi import FastAPI, Request
from pytz import timezone
from mangum import Mangum
from dotenv import load_dotenv
import os
import datetime
import requests
import json


load_dotenv()
token = os.environ.get('token')
app = FastAPI()


@app.get("/")
async def health():
    return {"test": "FastAPI Running"}


@app.post("/hook_check")
async def main(request: Request):
    json = await request.json()
    create_github_issue(json)
    return {"message": "Ok"}


def create_github_issue(res_json):
    sentry_issue_id = res_json["id"]
    project_name = res_json["project_name"]
    title = res_json["event"]["title"]
    error = res_json["message"]
    time = None
    error_detail = None
    for i in res_json["event"]["breadcrumbs"]["values"]:
        if i["level"] == "error":
            timestamp = i["timestamp"]
            time = datetime.datetime.fromtimestamp(timestamp, tz=timezone('Asia/Seoul'))
            error_detail = i["message"]

    sentry_url = res_json["url"]
    body = f"### sentry issue id : [{sentry_issue_id}]({sentry_url}) \
        ### 에러 내역 \
        - 발생시간 : {time} \
        - 에러 : {error} \
        - 상세 : {error_detail}"

    url = f"https://api.github.com/repos/lionrocket-inc/{project_name}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "title": title,
        "body": body,
        "labels": ["bug"],
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


handler = Mangum(app)
