from bson import ObjectId
from datetime import datetime, timedelta

from database.crud import create_user, get_user_by_team_and_name, get_user_generations, get_user_feedbacks
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

# 사용자 히스토리 조회 함수
def get_user_history(user_id: str, limit: int = 10):
    """
    사용자의 생성 히스토리와 피드백 히스토리를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 최대 개수
    
    Returns:
        dict: 생성 히스토리와 피드백 히스토리를 포함한 딕셔너리
    """
    try:
        # 생성 히스토리 조회
        generations = get_user_generations(user_id, limit=limit)
        
        # 피드백 히스토리 조회
        feedbacks = get_user_feedbacks(user_id, limit=limit)
        
        # 히스토리 데이터 정리
        history_data = {
            "generations": [],
            "feedbacks": [],
            "total_generations": len(generations),
            "total_feedbacks": len(feedbacks)
        }
        
        # 생성 히스토리 데이터 포맷팅
        for gen in generations:
            history_data["generations"].append({
                "id": gen.get("id", ""),
                "product_name": gen.get("product_info", {}).get("product_name", ""),
                "community": gen.get("attributes", {}).get("community", ""),
                "created_at": gen.get("created_at", ""),
                "content_count": len(gen.get("generated_contents", [])),
                "generated_contents": gen.get("generated_contents", []),  # 전체 데이터 포함
                "generation_type": gen.get("generation_type", "viral_copy"),  # generation_type 추가
                "product_info": gen.get("product_info", {}),  # product_info 전체 데이터 추가
                "attributes": gen.get("attributes", {})  # attributes 전체 데이터 추가
            })
        
        # 피드백 히스토리 데이터 포맷팅
        for feedback in feedbacks:
            history_data["feedbacks"].append({
                "id": feedback.get("id", ""),
                "feedback_text": feedback.get("feedback_text", ""),
                "created_at": feedback.get("created_at", ""),
                "feedback_type": feedback.get("feedback_type", "general")
            })
        
        return history_data
        
    except Exception as e:
        logger.error(f"[get_user_history] Error retrieving history for user_id={user_id}: {str(e)}")
        return {
            "generations": [],
            "feedbacks": [],
            "total_generations": 0,
            "total_feedbacks": 0
        }