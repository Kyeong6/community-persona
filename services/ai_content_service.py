"""
AI 콘텐츠 생성 서비스
프롬프트 로더와 Gemini LLM 서비스를 연결하는 통합 서비스
"""

import os
import sys
from typing import Dict, Any, List, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_service import GeminiLLMService, ContentRequest
from utils.prompt_loader import load_prompt_template
from utils.get_logger import logger

class AIContentService:
    """AI 콘텐츠 생성 통합 서비스"""
    
    def __init__(self):
        """초기화"""
        self.llm_service = GeminiLLMService()
        logger.info("AI 콘텐츠 서비스 초기화 완료")
    
    def generate_product_content(self, product_data: Dict[str, Any], 
                               community_tone: str = "mom_cafe",
                               emphasis_points: str = "quality",
                               content_length: str = "500") -> Dict[str, Any]:
        """상품 콘텐츠 생성"""
        try:
            # 프롬프트 템플릿 로드
            prompt_template = load_prompt_template("product_description")
            
            # 커뮤니티 톤 정보 로드
            tone_template = load_prompt_template("community_tone")
            tone_info = tone_template.get("tones", {}).get(community_tone, {})
            tone_description = tone_info.get("description", "친근하고 따뜻한 톤")
            
            # 강조사항 정보 로드
            emphasis_template = load_prompt_template("emphasis_points")
            emphasis_categories = emphasis_template.get("emphasis_categories", {})
            emphasis_info = emphasis_categories.get(emphasis_points, {})
            emphasis_description = emphasis_info.get("description", "품질과 내구성 강조")
            
            # 콘텐츠 요청 객체 생성
            request = ContentRequest(
                product_name=product_data.get("product_name", ""),
                category=product_data.get("category", ""),
                price=product_data.get("price", ""),
                features=product_data.get("features", ""),
                target_customer=product_data.get("target_customer", ""),
                community_tone=tone_description,
                emphasis_points=emphasis_description,
                content_length=content_length,
                additional_requirements=product_data.get("additional_requirements", "")
            )
            
            # LLM 서비스를 통한 콘텐츠 생성
            result = self.llm_service.generate_content(request, prompt_template)
            
            # 결과에 추가 정보 포함
            result.update({
                "community_tone": community_tone,
                "emphasis_points": emphasis_points,
                "content_length": content_length,
                "product_data": product_data
            })
            
            return result
            
        except Exception as e:
            logger.error(f"상품 콘텐츠 생성 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "model": "gemini",
                "generation_time": 0
            }
    
    def generate_multiple_tones(self, product_data: Dict[str, Any], 
                              emphasis_points: str = "quality",
                              content_length: str = "500") -> List[Dict[str, Any]]:
        """여러 톤으로 콘텐츠 생성"""
        try:
            # 사용 가능한 톤 목록
            tone_template = load_prompt_template("community_tone")
            available_tones = list(tone_template.get("tones", {}).keys())
            
            results = []
            
            for tone in available_tones:
                result = self.generate_product_content(
                    product_data=product_data,
                    community_tone=tone,
                    emphasis_points=emphasis_points,
                    content_length=content_length
                )
                
                # 톤별 결과에 ID 추가
                result["tone_id"] = len(results) + 1
                result["tone_name"] = tone_template.get("tones", {}).get(tone, {}).get("name", tone)
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"다중 톤 콘텐츠 생성 실패: {str(e)}")
            return []
    
    def get_available_tones(self) -> List[Dict[str, Any]]:
        """사용 가능한 톤 목록 반환"""
        try:
            tone_template = load_prompt_template("community_tone")
            tones = tone_template.get("tones", {})
            
            return [
                {
                    "key": key,
                    "name": info.get("name", key),
                    "description": info.get("description", ""),
                    "characteristics": info.get("characteristics", [])
                }
                for key, info in tones.items()
            ]
        except Exception as e:
            logger.error(f"톤 목록 로드 실패: {str(e)}")
            return []
    
    def get_available_emphasis_points(self) -> List[Dict[str, Any]]:
        """사용 가능한 강조사항 목록 반환"""
        try:
            emphasis_template = load_prompt_template("emphasis_points")
            emphasis_categories = emphasis_template.get("emphasis_categories", {})
            
            return [
                {
                    "key": key,
                    "name": info.get("name", key),
                    "description": info.get("description", ""),
                    "keywords": info.get("keywords", [])
                }
                for key, info in emphasis_categories.items()
            ]
        except Exception as e:
            logger.error(f"강조사항 목록 로드 실패: {str(e)}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 반환"""
        try:
            model_info = self.llm_service.get_model_info()
            available_tones = len(self.get_available_tones())
            available_emphasis = len(self.get_available_emphasis_points())
            
            return {
                "status": "active",
                "model_info": model_info,
                "available_tones": available_tones,
                "available_emphasis_points": available_emphasis,
                "prompts_loaded": True
            }
        except Exception as e:
            logger.error(f"서비스 상태 확인 실패: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

# 전역 인스턴스 생성
ai_content_service = AIContentService()
