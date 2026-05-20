
from datetime import datetime, timedelta, timezone
from pathlib import Path

from github_api import get_github

g = get_github()

DATA_DIR = "data"
TIMESTAMP_FILE = f"timestamp.txt"

def main(organization_name, repository_name):
    repo = g.get_repo(f"{organization_name}/{repository_name}")
    Path(f"{DATA_DIR}/{organization_name}_{repository_name}").mkdir(parents=True, exist_ok=True)
    timestamp_file = f"{DATA_DIR}/{organization_name}_{repository_name}/{TIMESTAMP_FILE}"

    timestamp = get_latest_timestamp(timestamp_file)
    update_latest_timestamp(timestamp_file, timestamp+timedelta(days=1))


def get_latest_timestamp(timestamp_file):
    try:
        with open(timestamp_file, "r") as f:
            return datetime.fromisoformat(f.read())
    except FileNotFoundError:
        return datetime.fromtimestamp(0, tz=timezone.utc)

def update_latest_timestamp(timestamp_file, timestamp):
    with open(timestamp_file, "w") as f:
        f.write(timestamp.isoformat())

if __name__ == "__main__":
    main("containers", "podman")