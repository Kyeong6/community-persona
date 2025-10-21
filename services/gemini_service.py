"""
Gemini API를 사용한 LLM 서비스
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
    productName: str
    price: str
    productAttribute: str
    event: str
    card: str
    coupon: str
    keyword: str
    etc: str
    bestCase: str = "베스트 케이스 예시"

class GeminiLLMService:
    """Gemini API를 사용한 LLM 서비스"""
    
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
        
        logger.info(f"Gemini LLM 서비스 초기화 완료 - 모델: {self.model_name}")
    
    def generate_content(self, formatted_prompt: str, product_name: str) -> Dict[str, Any]:
        """콘텐츠 생성"""
        try:
            logger.info(f"콘텐츠 생성 시작 - 상품: {product_name}")
            
            # Gemini API 호출 (재시도 로직 포함)
            response = self._call_gemini_with_retry(formatted_prompt)
            
            # JSON 응답 파싱 시도
            try:
                import json
                parsed_content = json.loads(response.text)
                
                # 응답 처리
                result = {
                    "success": True,
                    "content": parsed_content,
                    "raw_content": response.text,
                    "model": self.model_name,
                    "tokens_used": self._estimate_tokens(formatted_prompt + response.text),
                    "generation_time": time.time()
                }
                
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원본 텍스트 반환
                result = {
                    "success": True,
                    "content": {"error": "JSON 파싱 실패", "raw": response.text},
                    "raw_content": response.text,
                    "model": self.model_name,
                    "tokens_used": self._estimate_tokens(formatted_prompt + response.text),
                    "generation_time": time.time()
                }
            
            logger.info(f"콘텐츠 생성 완료 - 상품: {product_name}")
            return result
            
        except Exception as e:
            logger.error(f"콘텐츠 생성 실패 - 상품: {product_name}, 에러: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": {},
                "raw_content": "",
                "model": self.model_name,
                "generation_time": time.time()
            }
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
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
        }

# 전역 인스턴스 생성
llm_service = GeminiLLMService()
