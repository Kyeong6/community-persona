"""
입력 검증 유틸리티 함수들
"""

from typing import Tuple


def validate_input_form(product_name: str, price: str, community: str) -> Tuple[bool, str]:
    """
    입력 폼 유효성 검사
    
    Args:
        product_name: 상품명
        price: 가격
        community: 커뮤니티
        
    Returns:
        Tuple[bool, str]: (유효성 여부, 에러 메시지)
    """
    if not product_name or not product_name.strip():
        return False, "상품명을 입력해주세요."
    
    if not price or not price.strip():
        return False, "가격을 입력해주세요."
    
    if not community:
        return False, "타겟 커뮤니티를 선택해주세요."
    
    return True, ""


def validate_user_input(team_name: str, user_name: str) -> Tuple[bool, str]:
    """
    사용자 입력 유효성 검사
    
    Args:
        team_name: 팀명
        user_name: 사용자명
        
    Returns:
        Tuple[bool, str]: (유효성 여부, 에러 메시지)
    """
    if not team_name or not team_name.strip():
        return False, "팀명을 입력해주세요."
    
    if not user_name or not user_name.strip():
        return False, "사용자명을 입력해주세요."
    
    return True, ""