"""
사용자 관련 서비스
"""

import hashlib
import time
import sys
import os
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud import create_user, get_user
from database.models import User


def handle_user_login(team_name: str, user_name: str) -> str:
    """
    사용자 식별 및 등록
    
    Args:
        team_name: 팀명
        user_name: 사용자명
        
    Returns:
        user_id: 고유 사용자 ID
    """
    # 고유 user_id 생성 (팀명 + 사용자명 + 타임스탬프 기반)
    timestamp = str(int(time.time()))
    user_string = f"{team_name}_{user_name}_{timestamp}"
    user_id = hashlib.md5(user_string.encode()).hexdigest()[:12]
    
    # 사용자 생성
    create_user(team_name, user_name, user_id)
    
    return user_id


def get_user_info(user_id: str) -> User:
    """
    사용자 정보 조회
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        User: 사용자 정보
    """
    return get_user(user_id)


# 피드백 관련 함수는 content_service.py의 user_feedback() 함수 사용
