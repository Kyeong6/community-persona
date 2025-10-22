from bson import ObjectId

from database.crud import create_user
from utils.get_logger import logger

# 사용자 로그인 함수
def handle_user_login(team_name: str, user_name: str) -> str:
    
    # ObjectId를 사용한 고유 user_id 생성
    user_id = str(ObjectId())
    
    # 사용자 생성
    create_user(team_name, user_name, user_id)
    
    # 로그인 추적 로그
    logger.info(f"[handle_user_login] User logged in: user_id={user_id}, team_name={team_name}, user_name={user_name}")
    
    return user_id