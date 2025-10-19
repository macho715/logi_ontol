# 지속적 통합 개요

## 워크플로 요약
- `CI` 워크플로는 모든 push와 pull request에서 Python 3.13 환경으로 실행됩니다.
- 개발 도구를 사용하기 위해 프로젝트를 editable 모드로 `.[dev]`까지 설치합니다.
- 반복 실행 속도를 위해 `~/.cache/pip` 디렉터리를 캐시합니다.

## 품질 게이트
- Lint 잡은 `ruff check`, `black --check`, `isort --check-only`를 `logiontology/` 기준으로 수행합니다.
- Type-security 잡은 `mypy --strict`, `bandit -r src`, `pip-audit`로 품질을 검증합니다.
- Test 잡은 `coverage run -m pytest` 후 `coverage report --fail-under=70`으로 커버리지 기준을 확인합니다.
- 회귀 디버깅을 돕기 위해 커버리지 산출물을 업로드합니다.
