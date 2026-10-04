import os
from dotenv import load_dotenv
import requests

#load token from .env file
load_dotenv()

token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"Bearer {token}"}

url = "https://api.github.com/repos/fastapi/fastapi/actions/workflows/test.yml/runs?status=failure&per_page=5"
response = requests.get(url, headers=headers)

print(response.status_code)

# turn json into a python dictionary
data = response.json()

# workflow_runs holds a list of failed runs
# loop through that list one run at a time

for run in data["workflow_runs"]:
    # each run is a dictionary
    print("ID:", run["id"])
    print("Workflow:", run["name"])
    print("Title:", run["display_title"])
    print("Link:", run["html_url"])

    # blank line so each run is easy to tell apart
    print()