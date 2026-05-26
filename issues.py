from argparse import ArgumentParser
from datetime import datetime
from json import dump
from pathlib import Path

from github import GithubException

from github_api import get_github

g = get_github()

DATA_DIR = "data"
TIMESTAMP_FILE = f"timestamp.txt"

def main(organization_name, repository_name):
    repo = g.get_repo(f"{organization_name}/{repository_name}")
    repo_data_dir = f"{DATA_DIR}/{organization_name}_{repository_name}"
    Path(repo_data_dir).mkdir(parents=True, exist_ok=True)

    timestamp_file = f"{repo_data_dir}/{TIMESTAMP_FILE}"
    latest_timestamp = get_latest_timestamp(timestamp_file)

    try:
        issues = repo.get_issues(state="all", sort="updated", direction="asc", since=latest_timestamp)
        for issue in issues:
            issue_data = process_issue(issue)

            with open(f"{repo_data_dir}/{issue.number}.json", "w") as f:
                dump(issue_data, f, indent=4, ensure_ascii=False)

            update_latest_timestamp(timestamp_file, issue.updated_at)
    except GithubException as e:
        print(e)

def process_issue(issue):
    print(f"{issue.number}\t{issue.updated_at}\t{issue.title}")

    data = {}
    data["number"] = issue.number
    data["type"] = "pull_request" if issue.pull_request else "issue"
    data["title"] = issue.title
    data["user"] = issue.user.login
    data["body"] = issue.body
    data["comments"] = process_comments(issue)

    return data

def process_comments(issue):
    comments = []

    for comment in issue.get_comments():
        data = {}

        data["user"] = comment.user.login
        data["body"] = comment.body

        comments.append(data)

    return comments

def get_latest_timestamp(timestamp_file):
    try:
        with open(timestamp_file, "r") as f:
            return datetime.fromisoformat(f.read())
    except FileNotFoundError:
        return datetime.fromisoformat("2000-01-01T00:00:00Z")

def update_latest_timestamp(timestamp_file, timestamp):
    with open(timestamp_file, "w") as f:
        f.write(timestamp.isoformat())

def parse_arguments():
    parser = ArgumentParser(description="Save issue data from GitHub locally")
    parser.add_argument("organization", help="The organization name")
    parser.add_argument("repository", help="The repository name")
    return parser.parse_args()

if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments.organization, arguments.repository)