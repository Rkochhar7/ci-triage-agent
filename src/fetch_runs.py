import os
import csv
from dotenv import load_dotenv
import requests

#load token from .env file
load_dotenv()

token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"Bearer {token}"}

repos = [
    {"name": "fastapi/fastapi", "workflow": "test.yml"},
    {"name": "pydantic/pydantic", "workflow": "ci.yml"},
    {"name": "pytest-dev/pytest", "workflow": "test.yml"},
]

summary_jobs = ["test-alls-green", "check"]

rows = []

for r in repos:
    repo = r["name"]
    workflow = r["workflow"]

    print("=====", repo, "=====")

    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs"
    params = {"status": "failure", "per_page": 5}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Couldn't get runs for", repo, "- status", response.status_code)
        continue

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
        jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run['id']}/jobs"

        # ask GitHub for this run's jobs (same headers as before)
        jobs_response = requests.get(jobs_url, headers=headers, params={"per_page": 100})

        # turn the answer into a dictionary
        jobs_data = jobs_response.json()

        # loop through each job in this run
        for job in jobs_data["jobs"]:
            # only failed jobs, skipping the summary job
            if job["conclusion"] == "failure" and job["name"] not in summary_jobs:
                print("  Failed job:", job["id"], job["name"])

                # build the URL for this job's log
                log_url = f"https://api.github.com/repos/{repo}/actions/jobs/{job['id']}/logs"

                # download the log (it's plain text, not JSON)
                log_response = requests.get(log_url, headers=headers)
                log_text = log_response.text

                # split into lines and keep only the last 30
                lines = log_text.splitlines()
                # find where GitHub's cleanup starts, so we can cut it off
                cut = len(lines)    # default: keep everything if we don't find it
                for i in range(len(lines)):
                    if "Post job cleanup" in lines[i]:
                        cut = i
                        break

                # keep only lines before the cleanup, then the last 30 of those
                last_lines = lines[:cut][-30:]

                log_path = f"logs/{job['id']}.txt"
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines[:cut]))

                rows.append([repo, run["id"], job["id"], job["name"], run["display_title"], run["html_url"], log_path])

                # print each of those lines
                for line in last_lines:
                    print("    ", line)
                break

with open("runs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["repo", "run_id", "job_id", "job_name", "title", "url", "log_file"])
    writer.writerows(rows)