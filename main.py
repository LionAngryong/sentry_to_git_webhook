import datetime

from fastapi import FastAPI, Request
import requests
import json
import markdown
from mangum import Mangum

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
            time = datetime.datetime.fromtimestamp(timestamp)
            error_detail = i["message"]

    sentry_url = res_json["url"]
    body = markdown.markdown(f'''
        ### [{sentry_issue_id}]({sentry_url})

        ### 에러
        - 발생시간 : {time}
        - 에러 : {error}
        - 상세 : {error_detail}
    ''')

    token = "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"

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
