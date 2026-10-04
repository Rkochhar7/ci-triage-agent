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

    # build the URL for this run's jobs, using the run's id
    jobs_url = f"https://api.github.com/repos/fastapi/fastapi/actions/runs/{run['id']}/jobs"

    # ask GitHub for this run's jobs (same headers as before)
    jobs_response = requests.get(jobs_url, headers=headers)

    # turn the answer into a dictionary
    jobs_data = jobs_response.json()

    # loop through each job in this run
    for job in jobs_data["jobs"]:
        # only failed jobs, skipping the summary job
        if job["conclusion"] == "failure" and job["name"] != "test-alls-green":
            print("  Failed job:", job["id"], job["name"])
                        # build the URL for this job's log
            log_url = f"https://api.github.com/repos/fastapi/fastapi/actions/jobs/{job['id']}/logs"

            # download the log (it's plain text, not JSON)
            log_response = requests.get(log_url, headers=headers)
            log_text = log_response.text

            # split into lines and keep only the last 30
            lines = log_text.splitlines()
            last_lines = lines[-30:]

            # print each of those lines
            for line in last_lines:
                print("    ", line)
            break
