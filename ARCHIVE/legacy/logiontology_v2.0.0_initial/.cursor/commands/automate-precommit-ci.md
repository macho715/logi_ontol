# /automate pre-commit+ci
> Install hooks and verify CI locally.
```bash
pip install pre-commit && pre-commit install && pre-commit install --hook-type commit-msg
pytest -q
```
