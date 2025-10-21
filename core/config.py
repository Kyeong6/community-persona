import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리: community-persona-ai
BASE_DIR = Path(__file__).parent.parent

# 데이터베이스 경로
DATABASE_DIR = BASE_DIR / "data" / "database"
DATABASE_PATH = DATABASE_DIR / "database.db"

# # FAISS 벡터 데이터베이스
# FAISS_INDICES_DIR = BASE_DIR / "data" / "faiss_indices"

# 로그 경로
LOG_PATH = BASE_DIR / "logs"

# 프롬프트 경로
PROMPT_BASE_PATH = BASE_DIR / "prompts"


class Settings:
    
    # 데이터베이스 경로
    DATABASE_DIR = str(DATABASE_DIR)
    DATABASE_PATH = str(DATABASE_PATH)
    # FAISS_INDICES_DIR = str(FAISS_INDICES_DIR)
    
    # 로그 경로
    LOG_PATH = str(LOG_PATH)
    
    # 프롬프트 경로
    PROMPT_BASE_PATH = str(PROMPT_BASE_PATH)
    
    # Gemini API 설정
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("TOP_P", "0.8"))
    TOP_K = int(os.getenv("TOP_K", "40"))
    
    # 재시도 설정
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))

# 전역 설정 인스턴스
settings = Settings()
