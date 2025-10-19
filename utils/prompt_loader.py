import os
import yaml
import sys
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from utils.get_logger import logger

class PromptLoader:
    def __init__(self):
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()

    def _load_prompts(self):
        prompts_dir = settings.PROMPT_BASE_PATH
        
        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(prompts_dir, exist_ok=True)
        
        # 디렉토리가 비어있으면 빈 딕셔너리로 초기화
        if not os.path.exists(prompts_dir) or not os.listdir(prompts_dir):
            logger.info(f"Prompts directory is empty: {prompts_dir}")
            return
        
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".yaml"):
                try:
                    with open(os.path.join(prompts_dir, filename), "r", encoding="utf-8") as f:
                        prompt_data = yaml.safe_load(f)
                        # 파일 이름에서 확장자를 제거하고 키로 사용
                        prompt_key = os.path.splitext(filename)[0].lower()
                        self.prompts[prompt_key] = prompt_data
                except Exception as e:
                    logger.error(f"Error loading prompt file {filename}: {e}")

    def load_prompt(self, prompt_key: str) -> Any:
        if prompt_key not in self.prompts:
            logger.error(f"[load_prompt] Prompt key '{prompt_key}' not found")
            raise FileNotFoundError(f"Prompt key '{prompt_key}' not found")
        
        return self.prompts[prompt_key]


# 전역 인스턴스 생성
prompt_loader = PromptLoader()


def load_prompt_template(prompt_key: str) -> Any:
    """프롬프트 템플릿 로드 함수"""
    return prompt_loader.load_prompt(prompt_key)