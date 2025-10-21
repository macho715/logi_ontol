# Continuous Integration Overview

## Workflow Summary
- `CI` workflow runs on every push and pull request with Python 3.13.
- Installs project in editable mode with development extras to expose tooling.
- Caches `~/.cache/pip` to keep repeated runs fast.

## Quality Gates
- Lint job executes `ruff check`, `black --check`, and `isort --check-only` against `logiontology/`.
- Type-security job runs `mypy --strict`, `bandit -r src`, and `pip-audit` to maintain quality.
- Test job runs `coverage run -m pytest` followed by `coverage report --fail-under=70`.
- Coverage artifacts are uploaded to help debug regressions.
