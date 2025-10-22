import os
import yaml
from typing import Dict, Any

from core.config import settings
from utils.get_logger import logger

# 프롬프트 로더 클래스
class PromptLoader:
    def __init__(self):
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()

    # 프롬프트 로드 함수
    def _load_prompts(self):
        prompts_dir = settings.PROMPT_BASE_PATH
        
        # 프롬프트 파일 목록 로드
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".yaml"):
                try:
                    with open(os.path.join(prompts_dir, filename), "r", encoding="utf-8") as f:
                        # YAML 파일 로드
                        prompt_data = yaml.safe_load(f)
                        
                        # 파일 이름에서 확장자를 제거하고 키로 사용
                        prompt_key = os.path.splitext(filename)[0].lower()
                        self.prompts[prompt_key] = prompt_data
                except Exception as e:
                    logger.error(f"[_load_prompts] Error loading prompt file {filename}: {e}")

    def load_prompt(self, prompt_key: str) -> Any:
        # 프롬프트 키가 존재하지 않으면 오류 발생
        if prompt_key not in self.prompts:
            logger.error(f"[load_prompt] Prompt key '{prompt_key}' not found")
            raise FileNotFoundError(f"Prompt key '{prompt_key}' not found")
        
        return self.prompts[prompt_key]


# 전역 인스턴스 생성
prompt_loader = PromptLoader()

# 프롬프트 템플릿 로드 함수
def load_prompt_template(prompt_key: str) -> Any:
    return prompt_loader.load_prompt(prompt_key)