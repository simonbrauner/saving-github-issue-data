# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project stores GitHub issue and pull request data from Podman-related repositories as JSON files, updated daily. The primary use case is searching and analyzing issues across these repositories.

Tracked repositories:
- `podman-container-tools/buildah`
- `podman-container-tools/container-libs`
- `podman-container-tools/podman`
- `podman-container-tools/skopeo`

## Working with the Data

### Data Location and Naming

All issue data is in `data/issues/` with the naming pattern: `{organization}_{repository}_{number}.json`

Examples:
- `data/issues/podman-container-tools_podman_12345.json`
- `data/issues/podman-container-tools_buildah_678.json`

### JSON Schema

Each issue file contains:

```json
{
    "organization": "podman-container-tools",
    "repository": "podman",
    "number": 12345,
    "type": "issue" | "pull_request",
    "title": "Issue title",
    "state": "open" | "closed",
    "labels": ["bug", "enhancement"],
    "user": "github-username",
    "body": "Issue description text",
    "comments": [
        {
            "user": "commenter-username",
            "body": "Comment text"
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

**Key fields:**
- `type`: Distinguishes issues from pull requests
- `body`: Main issue description (empty string if none; carriage returns are removed)
- `comments`: All comments with user and text
- `cross_references`: Other issues that reference this one (extracted from timeline events)

### Common Search Patterns

**Find issues by keyword:**
```bash
grep -r "keyword" data/issues/ | grep -o '[^/]*\.json' | sort -u
```

**Find issues with specific label:**
```bash
grep -l '"bug"' data/issues/*.json
```

**Find open issues:**
```bash
grep -l '"state": "open"' data/issues/*.json
```

**Find issues by repository:**
```bash
ls data/issues/podman-container-tools_podman_*.json
```

**Search in issue bodies or comments (use jq):**
```bash
find data/issues -name "*.json" -exec jq 'select(.body | contains("search term"))' {} \;
```

**Count issues by repository:**
```bash
ls data/issues/ | cut -d_ -f1,2 | sort | uniq -c
```

### Analyzing Cross-References

The `cross_references` field shows which issues reference this one. This is useful for finding related discussions across repositories or tracking issue dependencies.

## Architecture

### Data Flow

1. **Timestamp-based Incremental Updates**: Issues are fetched sorted by `updated` in ascending order, starting from the timestamp stored in `data/timestamps/{organization}_{repository}_timestamp.txt`
2. **Per-Issue Checkpointing**: After each issue is saved to `data/issues/{organization}_{repository}_{number}.json`, the timestamp file is immediately updated with that issue's `updated_at` time
3. **Resumable Processing**: If a run stops early (timeout or rate limit), the next run continues from the last successfully saved issue

This design ensures no data loss if the GitHub Actions job hits its 10-minute timeout or the API rate limit.

### Key Files

- `issues.py`: Main script that fetches and processes issues for a single repository
- `github_api.py`: Handles GitHub authentication via PyGithub
- `update_issues.sh`: Orchestrates updates for all tracked repositories with 2-minute per-repo timeout
- `.github/workflows/update-issues.yml`: Scheduled daily at 04:13 UTC with 10-minute job timeout

### Data Processing

The `process_issue()` function in `issues.py` extracts:
- Basic metadata (number, type, title, state, labels, author)
- Body text with normalized line endings (carriage returns removed)
- All comments with user and body
- Cross-references from timeline events (issues that reference this one)

Cross-references are deduplicated by `(organization, repository, number)` tuple to avoid duplicates from multiple timeline events.

## Development Commands

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure GitHub token
cp .env.example .env
# Edit .env and set GITHUB_TOKEN to your personal access token
# For public repos, the 'public_repo' scope is sufficient
```

### Running

```bash
# Update a single repository
python issues.py <organization> <repository>

# Example:
python issues.py podman-container-tools podman

# Update all tracked repositories (uses 2-minute timeout per repo)
./update_issues.sh
```

### Testing Changes

When modifying the issue processing logic, test against a smaller repository or limit the date range to avoid fetching thousands of issues. You can manually edit a timestamp file to set a later start date.

## API Rate Limits

GitHub API allows 5,000 authenticated requests per hour. The script handles `GithubException` to gracefully exit when rate limited. The checkpointing system ensures progress is not lost.

## Adding a New Repository

To track a new repository:

1. Add the organization/repository to the list in README.md
2. Create an initial timestamp file: `echo "2000-01-01T00:00:00Z" > data/timestamps/{organization}_{repository}_timestamp.txt`
3. The next run of `update_issues.sh` will automatically pick it up based on timestamp files in `data/timestamps/`
