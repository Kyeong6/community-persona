from typing import Dict, List, Any

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
    community_key = product_data.get("community", "mam2bebe")
    
    
    # AI 서비스 호출
    result = ai_service.generate_product_content(
        product_data=product_data,
        community_key=community_key,
        content_length="500",
        user_id=user_id
    )
    
    if result['success']:
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
        # 콘텐츠 생성 실패 추적 로그
        logger.error(f"[generate_viral_copy] Content generation failed: user_id={user_id}, error={result.get('error', 'Unknown error')}")
    
    # 3. 콘텐츠 생성 기록 저장 (input_id 사용)
    content_id = create_content(
        input_id=input_id,
        parent_generate_id=None,
        generation_type="viral_copy",
        product_info=product_data,
        attributes={"community": community_key},
        generated_contents=generated_contents
    )
    
    # 콘텐츠 생성 성공 추적 로그 (content_id 생성 후)
    if result['success']:
        logger.info(f"[generate_viral_copy] Content generation successful: user_id={user_id}, content_id={content_id}")
    
    return {
        "generate_id": content_id,
        "input_id": input_id,
        "generated_contents": generated_contents
    }

# 결과물 채택 기록 (복사 버튼 클릭 시 호출)
def copy_action(user_id: str, generate_id: str, version_id: str, tone: str = None) -> bool:
    # 톤 선택 추적 로그 (분석용)
    logger.info(f"[copy_action] TONE_SELECTED: user_id={user_id}, generate_id={generate_id}, version_id={version_id}, tone={tone}")
    return True

# 피드백 수집
def user_feedback(user_id: str, feedback_text: str) -> bool:
    try:
        feedback_id = create_user_feedback(user_id, feedback_text)
        logger.info(f"[user_feedback] Feedback submitted: user_id={user_id}")
        return bool(feedback_id)
    except Exception as e:
        logger.error(f"[user_feedback] Error submitting feedback: user_id={user_id}, error={str(e)}")
        return False

# 재생성 요청
def regenerate_copy(user_id: str, generate_id: str, reason_text: str) -> Dict[str, Any]:
    # 원본 생성 정보 조회 (이전 생성 또는 최초 생성)
    original_content = get_content(generate_id)
    if not original_content:
        return {"error": "Original content not found"}
    
    # 재생성용 product_data 구성
    product_data = {
        **original_content['product_info'],
        "regenerate_reason": reason_text,
        "previous_contents": original_content['generated_contents']
    }
    
    # 커뮤니티 정보 추출 및 매핑
    community_key = original_content['attributes'].get("community", "mam2bebe")
    
    regenerate_community = f"regenerate_{community_key}"
    
    result = ai_service.generate_product_content(
        product_data=product_data,
        community_key=regenerate_community,
        user_id=user_id
    )
    
    if result['success']:
        generated_contents = result.get('generated_contents', [{
            'id': 1,
            'tone': 'AI 재생성',
            'text': result['content']
        }])
    else:
        generated_contents = [{
            'id': 1,
            'tone': '재생성 실패',
            'text': f"재생성 실패: {result.get('error', 'Unknown error')}"
        }]
        logger.error(f"[regenerate_copy] Regeneration failed: user_id={user_id}, error={result.get('error', 'Unknown error')}")
    
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
    
    # 재생성 성공 추적 로그 (content_id 생성 후)
    if result['success']:
        logger.info(f"[regenerate_copy] Regeneration successful: user_id={user_id}, new_content_id={content_id}")
    
    return {
        "generate_id": content_id,
        "input_id": original_content['input_id'],
        "generated_contents": generated_contents
    }

# 사용자의 콘텐츠 생성 이력 조회
def get_user_content_history(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    return get_user_contents(user_id, limit)


