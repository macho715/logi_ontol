"""
Configuration for MCP TTL Server
"""
import os
from pathlib import Path

# TTL 파일 경로 (기본: data/hvdc_data.ttl)
BASE_DIR = Path(__file__).parent.parent
TTL_PATH = os.getenv("TTL_PATH", str(BASE_DIR / "data" / "hvdc_data.ttl"))

# 서버 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

# CORS 설정 (GPT Custom Action 허용)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# HVDC 온톨로지 네임스페이스
HVDC_NAMESPACE = "http://samsung.com/project-logistics#"
HVDC_PREFIX = "hvdc"

# 캐싱 설정
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 300))  # 5분


