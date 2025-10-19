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


@dataclass
class UserFeedback:
    """사용자 피드백 모델"""
    id: str
    user_id: str
    feeback: str
    created_at: datetime


@dataclass
class Content:
    """콘텐츠 생성 기록 모델"""
    id: str
    user_id: str
    parent_generate_id: Optional[str]
    generation_type: str
    product_info: Dict[str, Any]
    attributes: Dict[str, Any]
    generated_contents: List[Dict[str, Any]]
    reason: Optional[str]
    created_at: datetime
