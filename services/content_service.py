"""
콘텐츠 관련 서비스
"""

import sys
import os
from typing import Dict, List, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud import (
    create_generation, get_generation, get_user_generations,
    create_copy_action, create_feedback, create_regenerate_log
)
from database.models import Generation
from .llm_service import generate_content_with_llm


def generate_viral_copy(user_id: str, product_info: Dict[str, Any], 
                       attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    문구 생성 요청
    
    Args:
        user_id: 사용자 ID
        product_info: 상품 정보 {product_name: str, price: int}
        attributes: 속성 정보 {community: str, category: str, emphasis_mode: str, emphasis_detail: str, best_case: str}
        
    Returns:
        Dict: {generate_id: str, generated_contents: List[Dict]}
    """
    # LLM을 사용한 콘텐츠 생성
    generated_contents = generate_content_with_llm(product_info, attributes)
    
    # DB에 생성 기록 저장
    generation = create_generation(user_id, product_info, attributes, generated_contents)
    
    return {
        "generate_id": generation.generate_id,
        "generated_contents": generated_contents
    }


def copy_action(user_id: str, generate_id: str, version_id: str) -> bool:
    """
    결과물 채택 기록 (복사 버튼 클릭 시 호출)
    
    Args:
        user_id: 사용자 ID
        generate_id: 생성 ID
        version_id: 버전 ID
        
    Returns:
        bool: 성공 여부
    """
    try:
        create_copy_action(user_id, generate_id, version_id, "copy")
        return True
    except Exception as e:
        print(f"복사 액션 로그 저장 실패: {e}")
        return False


def user_feedback(user_id: str, feedback_text: str) -> bool:
    """
    피드백 수집
    
    Args:
        user_id: 사용자 ID
        feedback_text: 피드백 텍스트
        
    Returns:
        bool: 성공 여부
    """
    try:
        create_feedback(user_id, feedback_text)
        return True
    except Exception as e:
        print(f"피드백 저장 실패: {e}")
        return False


def regenerate_copy(user_id: str, reason_text: str) -> Dict[str, Any]:
    """
    재생성 요청
    
    Args:
        user_id: 사용자 ID
        reason_text: 재생성 이유
        
    Returns:
        Dict: {generate_id: str, generated_contents: List[Dict]}
    """
    # 사용자의 최근 생성 기록 조회
    user_generations = get_user_generations(user_id, limit=1)
    if not user_generations:
        raise ValueError("재생성할 이전 생성 기록이 없습니다.")
    
    latest_generation = user_generations[0]
    
    # 재생성된 콘텐츠 생성
    new_contents = generate_content_with_llm(
        latest_generation.product_info, 
        latest_generation.attributes,
        reason_text
    )
    
    # 재생성 로그 기록
    create_regenerate_log(user_id, latest_generation.generate_id, reason_text, new_contents)
    
    # 새로운 생성 기록 저장
    new_generation = create_generation(
        user_id, 
        latest_generation.product_info, 
        latest_generation.attributes, 
        new_contents
    )
    
    return {
        "generate_id": new_generation.generate_id,
        "generated_contents": new_contents
    }


def get_user_content_history(user_id: str, limit: int = 5) -> List[Generation]:
    """
    사용자의 콘텐츠 생성 이력 조회
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 개수
        
    Returns:
        List[Generation]: 생성 이력 리스트
    """
    return get_user_generations(user_id, limit)
