"""
CRUD 작업 함수들
SQLite와 ChromaDB를 위한 데이터 조작 함수
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.connection import db
from database.models import User, UserFeedback, Content


def init_database():
    """데이터베이스 테이블 초기화"""
    conn = db.sqlite_conn
    
    # Users 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY NOT NULL,
            team_name TEXT NOT NULL,
            user_name TEXT NOT NULL,
            created_at DATETIME NOT NULL
        )
    """)
    
    # UserFeedback 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id TEXT PRIMARY KEY NOT NULL,
            user_id TEXT NOT NULL,
            feeback TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Contents 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contents (
            id TEXT PRIMARY KEY NOT NULL,
            user_id TEXT NOT NULL,
            parent_generate_id TEXT,
            generation_type TEXT NOT NULL,
            product_info TEXT NOT NULL,
            attributes TEXT NOT NULL,
            generated_contents TEXT NOT NULL,
            reason TEXT,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()


# User CRUD
def create_user(team_name: str, user_name: str, user_id: str) -> User:
    """사용자 생성"""
    conn = db.sqlite_conn
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO users (id, team_name, user_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, team_name, user_name, now))
    
    conn.commit()
    return User(user_id=user_id, team_name=team_name, user_name=user_name, created_at=now)


def get_user(user_id: str) -> Optional[User]:
    """사용자 조회"""
    conn = db.sqlite_conn
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if row:
        return User(
            user_id=row['id'],
            team_name=row['team_name'],
            user_name=row['user_name'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    return None


def create_user_feedback(user_id: str, feedback_text: str) -> str:
    """사용자 피드백 생성"""
    conn = db.sqlite_conn
    feedback_id = str(uuid.uuid4())
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO user_feedback (id, user_id, feeback, created_at)
        VALUES (?, ?, ?, ?)
    """, (feedback_id, user_id, feedback_text, now))
    
    conn.commit()
    return feedback_id


# Contents CRUD
def create_content(user_id: str, generation_type: str, product_info: Dict[str, Any], 
                  attributes: Dict[str, Any], generated_contents: List[Dict[str, Any]], 
                  parent_generate_id: Optional[str] = None, reason: Optional[str] = None) -> str:
    """콘텐츠 생성 기록 저장"""
    conn = db.sqlite_conn
    content_id = str(uuid.uuid4())
    now = datetime.now()
    
    import json
    conn.execute("""
        INSERT INTO contents (id, user_id, parent_generate_id, generation_type, 
                            product_info, attributes, generated_contents, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (content_id, user_id, parent_generate_id, generation_type,
          json.dumps(product_info, ensure_ascii=False),
          json.dumps(attributes, ensure_ascii=False),
          json.dumps(generated_contents, ensure_ascii=False),
          reason, now))
    
    conn.commit()
    return content_id


def get_content(content_id: str) -> Optional[Dict[str, Any]]:
    """콘텐츠 조회"""
    conn = db.sqlite_conn
    row = conn.execute("SELECT * FROM contents WHERE id = ?", (content_id,)).fetchone()
    
    if row:
        import json
        return {
            'id': row['id'],
            'user_id': row['user_id'],
            'parent_generate_id': row['parent_generate_id'],
            'generation_type': row['generation_type'],
            'product_info': json.loads(row['product_info']),
            'attributes': json.loads(row['attributes']),
            'generated_contents': json.loads(row['generated_contents']),
            'reason': row['reason'],
            'created_at': datetime.fromisoformat(row['created_at'])
        }
    return None


def get_user_contents(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """사용자의 콘텐츠 생성 기록 조회"""
    conn = db.sqlite_conn
    rows = conn.execute("""
        SELECT * FROM contents 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit)).fetchall()
    
    import json
    return [{
        'id': row['id'],
        'user_id': row['user_id'],
        'parent_generate_id': row['parent_generate_id'],
        'generation_type': row['generation_type'],
        'product_info': json.loads(row['product_info']),
        'attributes': json.loads(row['attributes']),
        'generated_contents': json.loads(row['generated_contents']),
        'reason': row['reason'],
        'created_at': datetime.fromisoformat(row['created_at'])
    } for row in rows]


