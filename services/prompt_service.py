import os
import sys
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import load_prompt_template
from utils.get_logger import get_logger

# 로거 설정
logger = get_logger()

# 프롬프트 생성 클래스
class PromptService:
    
    def __init__(self):
        self.available_communities = ["mam2bebe", "ppomppu", "fmkorea"]
    
    # 사용 가능한 커뮤니티 목록 반환
    def get_available_communities(self) -> list:
        return self.available_communities
    
    # 커뮤니티 프롬프트 로드
    def load_community_prompt(self, community: str) -> Dict[str, Any]:
        try:
            if community not in self.available_communities:
                logger.error(f"지원하지 않는 커뮤니티입니다: {community}")
                raise 
            
            prompt_template = load_prompt_template(community)
            return prompt_template
            
        except Exception as e:
            logger.error(f"프롬프트 로드 실패 - 커뮤니티: {community}, 에러: {str(e)}")
            raise
    
    def create_formatted_prompt(self, community: str, product_info: Dict[str, Any]) -> str:
        """포맷된 프롬프트 생성"""
        try:
            # 커뮤니티 프롬프트 로드
            prompt_template = self.load_community_prompt(community)
            
            # 변수 준비
            variables = {
                "productName": product_info.get("productName", ""),
                "price": product_info.get("price", ""),
                "productAttribute": product_info.get("productAttribute", ""),
                "event": product_info.get("event", ""),
                "card": product_info.get("card", ""),
                "coupon": product_info.get("coupon", ""),
                "keyword": product_info.get("keyword", ""),
                "etc": product_info.get("etc", ""),
                "bestCase": product_info.get("bestCase", "베스트 케이스 예시")
            }
            
            # system_prompt에서 변수 치환
            system_prompt = prompt_template.get("system_prompt", "")
            formatted_prompt = system_prompt.format(**variables)
            
            logger.info(f"포맷된 프롬프트 생성 완료 - 커뮤니티: {community}")
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"프롬프트 생성 실패 - 커뮤니티: {community}, 에러: {str(e)}")
            raise
    
    def get_community_info(self, community: str) -> Dict[str, Any]:
        """커뮤니티 정보 반환"""
        try:
            prompt_template = self.load_community_prompt(community)
            
            return {
                "name": prompt_template.get("name", ""),
                "description": prompt_template.get("description", ""),
                "version": prompt_template.get("version", ""),
                "input_variables": prompt_template.get("input_variables", {}),
                "community_style": prompt_template.get("community_style", {})
            }
            
        except Exception as e:
            logger.error(f"커뮤니티 정보 조회 실패 - 커뮤니티: {community}, 에러: {str(e)}")
            raise

# 전역 인스턴스 생성
prompt_service = PromptService()
