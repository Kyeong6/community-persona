import time
import google.generativeai as genai
from typing import Dict, Any, List
from dataclasses import dataclass

from core.config import settings
from utils.prompt_loader import load_prompt_template
from utils.get_logger import logger

@dataclass
class GenerationConfig:
    # 생성 설정
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 2048


# AI 서비스 통합 클래스
class AIService:
    
    # 초기화
    def __init__(self):
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
    
    # 상품 콘텐츠 생성
    def generate_product_content(self, product_data: Dict[str, Any], 
                               community_key: str = "mam2bebe",
                               content_length: str = "500") -> Dict[str, Any]:
        try:
            # 커뮤니티별 프롬프트 템플릿 로드
            prompt_template = load_prompt_template(community_key)
            
            # 데이터베이스 필드를 프롬프트 변수로 변환
            prompt_variables = {
                "productName": product_data.get("product_name", ""),
                "price": product_data.get("price", ""),
                "productAttribute": product_data.get("product_attribute", ""),
                "event": product_data.get("event", ""),
                "card": product_data.get("card", ""),
                "coupon": product_data.get("coupon", ""),
                "keyword": product_data.get("keyword", ""),
                "etc": product_data.get("etc", ""),
                "bestCase": product_data.get("best_case", ""),
                # 재생성 변수 추가
                "regenerateReason": product_data.get("regenerate_reason", ""),
                "previousContents": product_data.get("previous_contents", ""),
                # 프롬프트 템플릿 내부 변수들
                "role_definition": prompt_template.get("role_definition", ""),
                "guidelines": "\n".join(prompt_template.get("guidelines", [])),
                "community_style": prompt_template.get("community_style", {}),
                "output_format": prompt_template.get("output_format", ""),
                # community_style 딕셔너리의 개별 값들
                "community_style_core": prompt_template.get("community_style", {}).get("core", ""),
                "community_style_tone": prompt_template.get("community_style", {}).get("tone", ""),
                "community_style_characteristics": prompt_template.get("community_style", {}).get("characteristics", ""),
                "community_style_professional_terms": prompt_template.get("community_style", {}).get("professional_terms", "")
            }
            
            # 재생성 변수 디버깅 로그
            if product_data.get("regenerate_reason"):
                logger.info(f"재생성 이유: {product_data.get('regenerate_reason')}")
                logger.info(f"이전 콘텐츠 길이: {len(product_data.get('previous_contents', ''))}")
                logger.info(f"이전 콘텐츠 샘플: {product_data.get('previous_contents', '')[:200]}...")
            
            # 프롬프트 변수 치환
            system_prompt = prompt_template.get("system_prompt", "")
            formatted_system_prompt = system_prompt.format(**prompt_variables)
            
            # Gemini API 호출
            # logger.info(f"콘텐츠 생성 시작 - 상품: {prompt_variables['productName']}, 커뮤니티: {community_tone}")
            
            response = self._call_gemini_with_retry(formatted_system_prompt)
            
            # 응답 처리 - JSON 파싱 시도
            try:
                import json
                logger.info(f"AI 응답 원본: {response.text[:200]}...")  # 디버깅용 로그
                
                # JSON 응답인 경우 파싱
                response_text = response.text.strip()
                
                # JSON 부분만 추출 (```json ... ``` 형태일 수 있음)
                if '```json' in response_text:
                    start_idx = response_text.find('```json') + 7
                    end_idx = response_text.find('```', start_idx)
                    if end_idx != -1:
                        response_text = response_text[start_idx:end_idx].strip()
                elif '```' in response_text:
                    start_idx = response_text.find('```') + 3
                    end_idx = response_text.find('```', start_idx)
                    if end_idx != -1:
                        response_text = response_text[start_idx:end_idx].strip()
                
                if response_text.startswith('{'):
                    parsed_content = json.loads(response_text)
                    logger.info(f"JSON 파싱 성공: {list(parsed_content.keys())}")  # 디버깅용 로그
                    
                    # 톤별로 콘텐츠 분리
                    generated_contents = []
                    tone_mapping = {
                        'information': '정보전달형',
                        'review': '후기형', 
                        'humorous': '유머러스한 형',
                        'friendly': '친근한 톤'
                    }
                    
                    for i, (key, tone_name) in enumerate(tone_mapping.items(), 1):
                        if key in parsed_content and 'content' in parsed_content[key]:
                            generated_contents.append({
                                'id': i,
                                'tone': tone_name,
                                'text': parsed_content[key]['content']
                            })
                    
                    logger.info(f"생성된 콘텐츠 개수: {len(generated_contents)}")  # 디버깅용 로그
                    
                    # JSON에 예상된 키가 없으면 기본 처리
                    if not generated_contents:
                        logger.warning("JSON에 예상된 키가 없어서 기본 처리로 전환")
                        generated_contents = [{
                            'id': 1,
                            'tone': 'AI 생성',
                            'text': response.text
                        }]
                elif response_text.startswith('['):
                    # 배열 형태의 JSON 응답 처리 (재생성 시 발생할 수 있음)
                    parsed_content = json.loads(response_text)
                    logger.info(f"배열 형태 JSON 파싱 성공: {len(parsed_content)}개 항목")  # 디버깅용 로그
                    
                    generated_contents = []
                    for i, item in enumerate(parsed_content, 1):
                        if isinstance(item, dict) and 'tone' in item and 'text' in item:
                            generated_contents.append({
                                'id': i,
                                'tone': item['tone'],
                                'text': item['text']
                            })
                    
                    logger.info(f"배열에서 생성된 콘텐츠 개수: {len(generated_contents)}")  # 디버깅용 로그
                    
                    # 배열에 예상된 형식이 없으면 기본 처리
                    if not generated_contents:
                        logger.warning("배열에 예상된 형식이 없어서 기본 처리로 전환")
                        generated_contents = [{
                            'id': 1,
                            'tone': 'AI 생성',
                            'text': response.text
                        }]
                else:
                    logger.warning("JSON 형식이 아니어서 기본 처리로 전환")
                    # 일반 텍스트인 경우 기본 형식으로 변환
                    generated_contents = [{
                        'id': 1,
                        'tone': 'AI 생성',
                        'text': response.text
                    }]
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {e}")
                # JSON 파싱 실패 시 기본 형식으로 변환
                generated_contents = [{
                    'id': 1,
                    'tone': 'AI 생성',
                    'text': response.text
                }]
            
            result = {
                "success": True,
                "content": response.text,
                "generated_contents": generated_contents,
                "model": self.model_name,
                "tokens_used": self._estimate_tokens(formatted_system_prompt + response.text),
                "generation_time": time.time(),
                "community_tone": community_key,
                "content_length": content_length,
                "product_data": product_data
            }
            
            logger.info(f"콘텐츠 생성 완료 - 상품: {prompt_variables['productName']}")
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
    
    def get_available_communities(self) -> List[Dict[str, Any]]:
        """사용 가능한 커뮤니티 목록 반환"""
        try:
            import os
            prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")
            
            communities = []
            for filename in os.listdir(prompts_dir):
                if filename.endswith(".yaml") and not filename.endswith("_eng.yaml"):
                    community_key = filename.replace(".yaml", "")
                    try:
                        prompt_template = load_prompt_template(community_key)
                        communities.append({
                            "key": community_key,
                            "name": prompt_template.get("name", community_key),
                            "description": prompt_template.get("description", ""),
                            "version": prompt_template.get("version", "1.0")
                        })
                    except Exception as e:
                        logger.warning(f"커뮤니티 프롬프트 로드 실패: {community_key}, {e}")
            
            return communities
        except Exception as e:
            logger.error(f"커뮤니티 목록 로드 실패: {str(e)}")
            return []
    
    
    # Gemini API 호출 (재시도 로직 포함)
    def _call_gemini_with_retry(self, prompt: str) -> Any:
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
    
    # 토큰 수 추정
    def _estimate_tokens(self, text: str) -> int:

        return len(text) // 3
    
    # 서비스 상태 확인
    def get_service_status(self) -> Dict[str, Any]:
        try:
            available_communities = len(self.get_available_communities())
            
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
                "available_communities": available_communities,
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