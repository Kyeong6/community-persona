import os
import sys
from typing import Dict, List, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud import (
    create_content, get_content, get_user_contents,
    create_user_feedback, create_user_input
)
from services.ai_service import ai_service
from utils.get_logger import logger


# 커뮤니티 매핑 함수: 커뮤니티 표시명을 프롬프트 키로 변환
def get_community_key(community_display_name: str) -> str:

    community_mapping = {
        "맘이베베": "mam2bebe",
        "뽐뿌": "ppomppu", 
        "에펨코리아": "fmkorea",    
    }

    return community_mapping.get(community_display_name, "mam2bebe")


# 커뮤니티 매핑 함수: 프롬프트 키를 커뮤니티 표시명으로 변환
def get_community_display_name(community_key: str) -> str:
    display_mapping = {
        "mam2bebe": "맘이베베",
        "ppomppu": "뽐뿌",
        "fmkorea": "에펨코리아"
    }
    return display_mapping.get(community_key, "맘이베베")


# 문구 생성 요청 함수
def generate_viral_copy(user_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:

    # 1. 사용자 입력 정보 저장
    input_id = create_user_input(
        user_id=user_id,
        product_name=product_data.get("product_name", ""),
        price=product_data.get("price"),
        product_attribute=product_data.get("product_attribute"),
        event=product_data.get("event"),
        card=product_data.get("card"),
        coupon=product_data.get("coupon"),
        keyword=product_data.get("keyword"),
        etc=product_data.get("etc"),
        community=product_data.get("community", ""),
        best_case=product_data.get("best_case")
    )
    
    # 2. AI 서비스를 사용한 콘텐츠 생성
    community_display = product_data.get("community", "맘이베베")
    community_key = get_community_key(community_display)
    
    # AI 서비스 호출
    result = ai_service.generate_product_content(
        product_data=product_data,
        community_key=community_key,
        content_length="500"
    )
    
    if result['success']:
        # 성공 시 AI 서비스에서 반환된 generated_contents 사용
        generated_contents = result.get('generated_contents', [{
            'id': 1,
            'tone': 'AI 생성',
            'text': result['content']
        }])
    else:
        # 실패 시 빈 결과
        generated_contents = [{
            'id': 1,
            'tone': '생성 실패',
            'text': f"콘텐츠 생성 실패: {result.get('error', 'Unknown error')}"
        }]
    
    # 3. 콘텐츠 생성 기록 저장 (input_id 사용)
    content_id = create_content(
        input_id=input_id,
        parent_generate_id=None,
        generation_type="viral_copy",
        product_info=product_data,
        attributes={"community": community_key},
        generated_contents=generated_contents
    )
    
    return {
        "generate_id": content_id,
        "input_id": input_id,
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
    try:
        feedback_id = create_user_feedback(user_id, feedback_text)
        return bool(feedback_id)  # feedback_id가 존재하면 True
    except Exception as e:
        logger.error(f"피드백 저장 실패: {str(e)}")
        return False


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
    import json
    
    # 원본 생성 정보 조회 (이전 생성 또는 최초 생성)
    original_content = get_content(generate_id)
    if not original_content:
        return {"error": "원본 생성 정보를 찾을 수 없습니다."}
    
    logger.info(f"재생성 시작 - generate_id: {generate_id}, reason: {reason_text}")
    logger.info(f"원본 콘텐츠 개수: {len(original_content['generated_contents'])}")
    
    # 이전 문구들을 JSON 형태로 변환 (직전 생성 내용 사용)
    previous_contents = json.dumps(original_content['generated_contents'], ensure_ascii=False)
    logger.info(f"이전 콘텐츠 길이: {len(previous_contents)}")
    
    # 재생성용 product_data 구성
    product_data = {
        **original_content['product_info'],
        "regenerate_reason": reason_text,
        "previous_contents": previous_contents
    }
    
    # 커뮤니티 정보 추출 및 매핑
    community_key = original_content['attributes'].get("community", "mam2bebe")
    
    # 재생성 전용 프롬프트 사용
    regenerate_community = f"regenerate_{community_key}"
    logger.info(f"재생성 프롬프트 사용: {regenerate_community}")
    
    # AI 서비스 호출 (재생성 전용 프롬프트 사용)
    result = ai_service.generate_product_content(
        product_data=product_data,
        community_key=regenerate_community
    )
    
    if result['success']:
        # 성공 시 AI 서비스에서 반환된 generated_contents 사용
        generated_contents = result.get('generated_contents', [{
            'id': 1,
            'tone': 'AI 재생성',
            'text': result['content']
        }])
    else:
        # 실패 시 빈 결과
        generated_contents = [{
            'id': 1,
            'tone': '재생성 실패',
            'text': f"재생성 실패: {result.get('error', 'Unknown error')}"
        }]
    
    # 재생성된 콘텐츠에 이유 추가
    for content in generated_contents:
        content["regenerate_reason"] = reason_text
    
    # 새로운 콘텐츠 생성 기록 저장
    content_id = create_content(
        input_id=original_content['input_id'],
        parent_generate_id=generate_id,
        generation_type="regenerate",
        product_info=product_data,
        attributes={"community": community_key, "regenerate_reason": reason_text},
        generated_contents=generated_contents,
        reason=reason_text
    )
    
    return {
        "generate_id": content_id,
        "input_id": original_content['input_id'],
        "generated_contents": generated_contents
    }


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


