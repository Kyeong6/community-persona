"""
프롬프트 생성 서비스
커뮤니티별 프롬프트를 로드하고 변수를 치환하여 최종 프롬프트를 생성
"""

import os
import sys
from typing import Dict, Any, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import load_prompt_template
from utils.get_logger import logger

class PromptService:
    """프롬프트 생성 서비스"""
    
    def __init__(self):
        """초기화"""
        self.available_communities = ["mam2bebe", "ppomppu", "fmkorea"]
        logger.info("프롬프트 서비스 초기화 완료")
    
    def get_available_communities(self) -> list:
        """사용 가능한 커뮤니티 목록 반환"""
        return self.available_communities
    
    def load_community_prompt(self, community: str) -> Dict[str, Any]:
        """커뮤니티 프롬프트 로드"""
        try:
            if community not in self.available_communities:
                raise ValueError(f"지원하지 않는 커뮤니티입니다: {community}")
            
            prompt_template = load_prompt_template(community)
            logger.info(f"커뮤니티 프롬프트 로드 완료: {community}")
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
