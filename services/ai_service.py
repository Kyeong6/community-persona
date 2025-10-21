"""
AI 서비스 통합 모듈
Gemini API, 프롬프트 관리, 콘텐츠 생성을 통합한 서비스
"""

import os
import sys
import time
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from utils.prompt_loader import load_prompt_template
from utils.get_logger import logger

@dataclass
class GenerationConfig:
    """생성 설정"""
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 2048

@dataclass
class ContentRequest:
    """콘텐츠 생성 요청"""
    product_name: str
    category: str
    price: str
    features: str
    target_customer: str
    community_tone: str
    emphasis_points: str
    content_length: str
    additional_requirements: str = ""

class AIService:
    """AI 서비스 통합 클래스"""
    
    def __init__(self):
        """초기화"""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        
        # API 키 검증
        if not self.api_key:
            logger.error("Gemini API 키가 설정되지 않았습니다.")
            raise ValueError("GEMINI_API_KEY 환경 변수를 설정해주세요.")
        
        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        
        # 모델 초기화
        self.model = genai.GenerativeModel(self.model_name)
        
        # 생성 설정
        self.generation_config = GenerationConfig(
            temperature=settings.TEMPERATURE,
            top_p=settings.TOP_P,
            top_k=settings.TOP_K,
            max_output_tokens=settings.MAX_TOKENS
        )
        
        logger.info(f"AI 서비스 초기화 완료 - 모델: {self.model_name}")
    
    def generate_content(self, request: ContentRequest, prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """콘텐츠 생성"""
        try:
            # 프롬프트 구성
            system_prompt = prompt_template.get("system_prompt", "")
            user_prompt = prompt_template.get("user_prompt", "")
            
            # 사용자 프롬프트에 변수 치환
            formatted_user_prompt = user_prompt.format(
                product_name=request.product_name,
                category=request.category,
                price=request.price,
                features=request.features,
                target_customer=request.target_customer,
                community_tone=request.community_tone,
                emphasis_points=request.emphasis_points,
                content_length=request.content_length,
                additional_requirements=request.additional_requirements
            )
            
            # 전체 프롬프트 구성
            full_prompt = f"{system_prompt}\n\n{formatted_user_prompt}"
            
            logger.info(f"콘텐츠 생성 시작 - 상품: {request.product_name}")
            
            # Gemini API 호출 (재시도 로직 포함)
            response = self._call_gemini_with_retry(full_prompt)
            
            # 응답 처리
            result = {
                "success": True,
                "content": response.text,
                "model": self.model_name,
                "tokens_used": self._estimate_tokens(full_prompt + response.text),
                "generation_time": time.time()
            }
            
            logger.info(f"콘텐츠 생성 완료 - 상품: {request.product_name}")
            return result
            
        except Exception as e:
            logger.error(f"콘텐츠 생성 실패 - 상품: {request.product_name}, 에러: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "model": self.model_name,
                "generation_time": time.time()
            }
    
    def generate_product_content(self, product_data: Dict[str, Any], 
                               community_tone: str = "mom_cafe",
                               emphasis_points: str = "quality",
                               content_length: str = "500") -> Dict[str, Any]:
        """상품 콘텐츠 생성 (통합 메서드)"""
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
            
            # 콘텐츠 생성
            result = self.generate_content(request, prompt_template)
            
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
    
    def _call_gemini_with_retry(self, prompt: str) -> Any:
        """재시도 로직이 포함된 Gemini API 호출"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.generation_config.temperature,
                        top_p=self.generation_config.top_p,
                        top_k=self.generation_config.top_k,
                        max_output_tokens=self.generation_config.max_output_tokens
                    )
                )
                
                if response.text:
                    return response
                else:
                    raise ValueError("빈 응답을 받았습니다.")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API 호출 실패 (시도 {attempt + 1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # 지수 백오프
                else:
                    raise last_error
        
        raise last_error
    
    def _estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (대략적)"""
        # 한국어 기준 대략적인 토큰 수 추정
        return len(text) // 3
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 반환"""
        try:
            available_tones = len(self.get_available_tones())
            available_emphasis = len(self.get_available_emphasis_points())
            
            return {
                "status": "active",
                "model_info": {
                    "model_name": self.model_name,
                    "api_key_configured": bool(self.api_key),
                    "generation_config": {
                        "temperature": self.generation_config.temperature,
                        "top_p": self.generation_config.top_p,
                        "top_k": self.generation_config.top_k,
                        "max_output_tokens": self.generation_config.max_output_tokens
                    },
                    "retry_settings": {
                        "max_retries": self.max_retries,
                        "retry_delay": self.retry_delay
                    }
                },
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
ai_service = AIService()
