# Saving issue data from GitHub locally

GitHub API: https://docs.github.com/en/rest/issues/issues?apiVersion=2026-03-10#list-repository-issues

Python library: https://pygithub.readthedocs.io/en/stable/reference.html

5000 requests/hour.

## Proof of concept

### `issues.py`

Iterates over issue data in ascending order sorted by last update, stops when the limit is reached and stores the last updated timestamp, so that on the next run it can easily continue where it left off. Additionally, this could be useful when updating the data later.
