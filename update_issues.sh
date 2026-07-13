#!/bin/bash

set -euo pipefail
shopt -s nullglob

TIMESTAMP_DIR='data/timestamps'
TIMEOUT='20s'

for timestamp_file in "$TIMESTAMP_DIR"/*; do
    basename="${timestamp_file##*/}"
    basename="${basename%_timestamp.txt}"

    organization="${basename%%_*}"
    repository="${basename#*_}"

    echo "Updating issues for $organization/$repository (timeout: $TIMEOUT)..."

    timeout "$TIMEOUT" python3 issues.py "$organization" "$repository" && echo "Done." || echo "Timeout reached."
done
