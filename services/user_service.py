from bson import ObjectId

from database.crud import create_user, get_user_by_team_and_name
from utils.get_logger import logger

# 사용자 로그인 함수
def handle_user_login(team_name: str, user_name: str) -> str:
    
    # 기존 사용자 확인
    existing_user = get_user_by_team_and_name(team_name, user_name)
    if existing_user:
        user_id = existing_user['id']
        logger.info(f"[handle_user_login] Existing user logged in: user_id={user_id}, team_name={team_name}, user_name={user_name}")
        return user_id
    
    # 새로운 사용자 생성
    user_id = str(ObjectId())
    create_user(team_name, user_name, user_id)
    
    # 로그인 추적 로그
    logger.info(f"[handle_user_login] New user logged in: user_id={user_id}, team_name={team_name}, user_name={user_name}")
    
    return user_id