# Saving GitHub issue data locally

Issue and pull request data from GitHub repositories stored as JSON files.

Tracked repositories:

- `podman-container-tools/buildah`
- `podman-container-tools/container-libs`
- `podman-container-tools/podman`
- `podman-container-tools/skopeo`

The updates are ran daily via GitHub action. Updates are incremental: issues are fetched sorted by `updated` in ascending order, starting from the timestamp stored in `data/timestamps/`. After each issue is saved, the timestamp file is updated. If a run stops early (timeout or rate limit), the next run continues where it left off.


## Data layout

```
data/
├── issues/
│   └── {organization}_{repository}_{number}.json
└── timestamps/
    └── {organization}_{repository}_timestamp.txt
```

Each issue file is a JSON object with this structure:

```json
{
    "organization": "podman-container-tools",
    "repository": "skopeo",
    "number": 2345,
    "type": "pull_request",
    "title": "Add a feature",
    "state": "open",
    "labels": [],
    "user": "user",
    "body": "...",
    "comments": [
        {
            "user": "user",
            "body": "..."
        }
    ],
    "cross_references": [
        {
            "organization": "podman-container-tools",
            "repository": "container-libs",
            "number": 5432
        }
    ]
}
```

| Field | Type | Description |
|---|---|---|
| `organization` | string | GitHub organization or user that owns the repository |
| `repository` | string | Repository name |
| `number` | integer | Issue or pull request number |
| `type` | string | `"issue"` or `"pull_request"` |
| `title` | string | Issue title |
| `state` | string | `"open"` or `"closed"` |
| `labels` | array of strings | Label names |
| `user` | string | Login of the issue author |
| `body` | string | Issue body text (`""` if empty); carriage returns are removed |
| `comments` | array of objects | Each object has `user` (string) and `body` (string) |
| `cross_references` | array of objects | Issues that reference this one in the timeline; each object has `organization`, `repository`, and `number` |

The timestamp file for each repository contains a single ISO 8601 datetime (for example `2026-07-13T08:51:15+00:00`) marking the `updated_at` time of the last successfully saved issue.

## Usage

GitHub personal access token is required. For public repositories, the `public_repo` scope is enough.

### Single repository

```bash
python issues.py <organization> <repository>
```

### All repositories

```bash
./update_issues.sh
```

## Rate limits

Authenticated requests are limited to 5,000 per hour. See the [GitHub REST API docs](https://docs.github.com/en/rest/issues/issues#list-repository-issues) and [PyGithub](https://pygithub.readthedocs.io/en/stable/reference.html).
