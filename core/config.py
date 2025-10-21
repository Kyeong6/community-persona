"""
설정 관리
데이터베이스 경로 및 기타 설정
"""

import os
from pathlib import Path

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent

# 데이터베이스 설정
DATABASE_DIR = BASE_DIR / "data" / "database"
DATABASE_PATH = DATABASE_DIR / "database.db"

# FAISS 벡터 데이터베이스 설정
FAISS_INDICES_DIR = BASE_DIR / "data" / "faiss_indices"

# 로그 설정
LOG_PATH = BASE_DIR / "logs"

# 프롬프트 설정
PROMPT_BASE_PATH = BASE_DIR / "prompts"

# 설정 클래스
class Settings:
    """애플리케이션 설정"""
    
    # 데이터베이스 경로
    DATABASE_DIR = str(DATABASE_DIR)
    DATABASE_PATH = str(DATABASE_PATH)
    FAISS_INDICES_DIR = str(FAISS_INDICES_DIR)
    
    # 로그 경로
    LOG_PATH = str(LOG_PATH)
    
    # 프롬프트 경로
    PROMPT_BASE_PATH = str(PROMPT_BASE_PATH)
    
    # 기타 설정
    DEBUG = True
    LOG_LEVEL = "INFO"

# 전역 설정 인스턴스
settings = Settings()
