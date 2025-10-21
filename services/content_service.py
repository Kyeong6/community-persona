"""
콘텐츠 관련 서비스
"""

import sys
import os
from typing import Dict, List, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud import (
    create_content, get_content, get_user_contents,
    create_user_feedback
)
from .ai_service import ai_service


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
    # AI 서비스를 사용한 콘텐츠 생성
    # 기존 attributes를 새로운 형식으로 변환
    community_tone = attributes.get("community", "mom_cafe")
    emphasis_points = attributes.get("emphasis_mode", "quality")
    
    # AI 서비스 호출
    result = ai_service.generate_product_content(
        product_data=product_info,
        community_tone=community_tone,
        emphasis_points=emphasis_points,
        content_length="500"
    )
    
    if result['success']:
        # 성공 시 기존 형식으로 변환
        generated_contents = [{
            'id': 1,
            'tone': 'AI 생성',
            'text': result['content']
        }]
    else:
        # 실패 시 빈 결과
        generated_contents = [{
            'id': 1,
            'tone': '생성 실패',
            'text': f"콘텐츠 생성 실패: {result.get('error', 'Unknown error')}"
        }]
    
    # DB에 생성 기록 저장
    content_id = create_content(user_id, "viral_copy", product_info, attributes, generated_contents)
    
    return {
        "generate_id": content_id,
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
    # TODO: 복사 액션 로그 구현
    return True


def user_feedback(user_id: str, feedback_text: str) -> bool:
    """
    피드백 수집
    
    Args:
        user_id: 사용자 ID
        feedback_text: 피드백 텍스트
        
    Returns:
        bool: 성공 여부
    """
    return create_user_feedback(user_id, feedback_text)


def regenerate_copy(user_id: str, generate_id: str, reason_text: str) -> Dict[str, Any]:
    """
    재생성 요청
    
    Args:
        user_id: 사용자 ID
        generate_id: 원본 생성 ID
        reason_text: 재생성 이유
        
    Returns:
        Dict: {generate_id: str, generated_contents: List[Dict]}
    """
    # 원본 생성 정보 조회
    original_content = get_content(generate_id)
    if not original_content:
        return {"error": "원본 생성 정보를 찾을 수 없습니다."}
    
    # 새로운 콘텐츠 생성
    return generate_viral_copy(user_id, original_content.product_info, 
                             original_content.attributes)


def get_user_content_history(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    사용자의 콘텐츠 생성 이력 조회
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 개수
        
    Returns:
        List[Dict]: 생성 이력 리스트
    """
    return get_user_contents(user_id, limit)
