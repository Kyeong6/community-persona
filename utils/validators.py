from typing import Tuple

# 사용자 입력 유효성 검사
def validate_user_input(team_name: str, user_name: str) -> Tuple[bool, str]:
    
    if not team_name or not team_name.strip():
        return False, "팀명을 입력해주세요."
    
    if not user_name or not user_name.strip():
        return False, "사용자명을 입력해주세요."
    
    return True, ""

# 입력 폼 유효성 검사
def validate_input_form(product_name: str, community: str) -> Tuple[bool, str]:
    
    if not product_name or not product_name.strip():
        return False, "상품명을 입력해주세요."
    
    if not community:
        return False, "타겟 커뮤니티를 선택해주세요."
    
    return True, ""