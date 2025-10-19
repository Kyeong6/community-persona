"""
LLM 관련 서비스
"""

from typing import Dict, List, Any


def generate_content_with_llm(product_info: Dict[str, Any], attributes: Dict[str, Any], 
                             reason_text: str = "") -> List[Dict[str, Any]]:
    """
    LLM을 사용한 콘텐츠 생성 (임시 구현)
    
    Args:
        product_info: 상품 정보
        attributes: 속성 정보
        reason_text: 재생성 이유 (선택사항)
        
    Returns:
        List[Dict]: 생성된 콘텐츠 리스트
    """
    # TODO: 실제 LLM API 호출 구현
    # 현재는 기존 로직을 사용
    
    product_name = product_info.get("product_name", "상품명")
    price = product_info.get("price", "가격")
    community = attributes.get("community", "ppomppu")
    emphasis_details = [attributes.get("emphasis_detail", "")]
    
    # 커뮤니티별 톤 조정
    community_tones = {
        'ppomppu': ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'],
        'fmkorea': ['정보 전달형', '후기형', '친근한 톤', '유머러스한 톤'],
        'womad': ['후기형', '친근한 톤', '정보 전달형', '유머러스한 톤']
    }
    
    tones = community_tones.get(community, ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'])
    
    # 강조사항 텍스트 생성
    emphasis_text = '\n'.join([f"• {detail}" for detail in emphasis_details if detail])
    
    # 재생성 이유가 있으면 추가
    if reason_text:
        emphasis_text += f"\n• 재생성 요청: {reason_text}"
    
    # 각 톤별 원고 생성
    contents = []
    
    # 1. 친근한 톤
    contents.append({
        'id': 1,
        'tone': '친근한 톤',
        'text': f"""{product_name} 이거 진짜 대박이에요 ㄷㄷ

작년에 {price}에 샀는데 지금 보니까 또 세일하네요.
이 가격에 이 퀄리티면 가성비 ㅇㅈ?

{emphasis_text}

놓치면 후회할 듯... 저는 재구매 각입니다 👍"""
    })
    
    # 2. 정보 전달형
    contents.append({
        'id': 2,
        'tone': '정보 전달형',
        'text': f"""{product_name} 특가 정보 공유합니다.

가격: {price}

{emphasis_text}

비교해보니 역대급 가격인 것 같아서 올립니다.
필요하신 분들 참고하세요!"""
    })
    
    # 3. 후기형
    contents.append({
        'id': 3,
        'tone': '후기형',
        'text': f"""{product_name} 쓴지 3개월 됐는데 후기 남깁니다.

솔직히 처음엔 {price} 주고 사기 좀 망설였는데
지금은 완전 만족 중이에요 ㅎㅎ

{emphasis_text}

지금 또 세일한다길래 주변에 추천하려고 글 올려요.
고민하시는 분들한테는 강추!"""
    })
    
    # 4. 유머러스한 톤
    contents.append({
        'id': 4,
        'tone': '유머러스한 톤',
        'text': f"""{product_name} {price}이라니...

(이거 사야되나 말아야되나 고민중)

{emphasis_text}

지갑: 안돼...😭
나: 어차피 살 거 지금 사는 게 이득 아니야?
지갑: ...💸

결국 또 질렀습니다 여러분 ㅋㅋㅋ
같이 망하실 분? 🙋‍♀️"""
    })
    
    return contents
