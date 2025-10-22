import os
import sys
from bson import ObjectId

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud import create_user

# 사용자 로그인 함수
def handle_user_login(team_name: str, user_name: str) -> str:
    
    # ObjectId를 사용한 고유 user_id 생성
    user_id = str(ObjectId())
    
    # 사용자 생성
    create_user(team_name, user_name, user_id)
    
    return user_id