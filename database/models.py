"""
데이터베이스 모델 정의
SQLite와 ChromaDB를 위한 데이터 구조
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class User:
    """사용자 정보 모델"""
    user_id: str
    team_name: str
    user_name: str
    created_at: datetime
    feedback: Optional[str] = None


@dataclass
class Generation:
    """문구 생성 기록 모델"""
    generate_id: str
    user_id: str
    product_info: Dict[str, Any]
    attributes: Dict[str, Any]
    generated_contents: List[Dict[str, Any]]
    created_at: datetime


@dataclass
class CopyAction:
    """복사 액션 로그 모델"""
    action_id: str
    user_id: str
    generate_id: str
    version_id: str
    action_type: str  # 'copy', 'regenerate'
    created_at: datetime


@dataclass
class Feedback:
    """피드백 모델"""
    feedback_id: str
    user_id: str
    feedback_text: str
    created_at: datetime


@dataclass
class RegenerateLog:
    """재생성 로그 모델"""
    regenerate_id: str
    user_id: str
    generate_id: str
    reason_text: str
    new_contents: List[Dict[str, Any]]
    created_at: datetime
