#!/usr/bin/env bash
# Run the same checks as the branch workflow, before you push.
set -euo pipefail

ruff check .
ruff format --check .
mypy app
pytest --cov