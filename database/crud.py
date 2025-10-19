"""
CRUD 작업 함수들
SQLite와 ChromaDB를 위한 데이터 조작 함수
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.connection import db
from database.models import User, Generation, CopyAction, Feedback, RegenerateLog


def init_database():
    """데이터베이스 테이블 초기화"""
    conn = db.sqlite_conn
    
    # Users 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            team_name TEXT NOT NULL,
            user_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            feedback TEXT
        )
    """)
    
    # Generations 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            generate_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_info TEXT NOT NULL,
            attributes TEXT NOT NULL,
            generated_contents TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Copy Actions 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS copy_actions (
            action_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            generate_id TEXT NOT NULL,
            version_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (generate_id) REFERENCES generations (generate_id)
        )
    """)
    
    # Feedbacks 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            feedback_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            feedback_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Regenerate Logs 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS regenerate_logs (
            regenerate_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            generate_id TEXT NOT NULL,
            reason_text TEXT NOT NULL,
            new_contents TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (generate_id) REFERENCES generations (generate_id)
        )
    """)
    
    conn.commit()


# User CRUD
def create_user(team_name: str, user_name: str, user_id: str) -> User:
    """사용자 생성"""
    conn = db.sqlite_conn
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO users (user_id, team_name, user_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, team_name, user_name, now))
    
    conn.commit()
    return User(user_id=user_id, team_name=team_name, user_name=user_name, created_at=now)


def get_user(user_id: str) -> Optional[User]:
    """사용자 조회"""
    conn = db.sqlite_conn
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    
    if row:
        return User(
            user_id=row['user_id'],
            team_name=row['team_name'],
            user_name=row['user_name'],
            created_at=datetime.fromisoformat(row['created_at']),
            feedback=row['feedback']
        )
    return None


def update_user_feedback(user_id: str, feedback_text: str) -> bool:
    """사용자 피드백 업데이트"""
    conn = db.sqlite_conn
    cursor = conn.execute(
        "UPDATE users SET feedback = ? WHERE user_id = ?",
        (feedback_text, user_id)
    )
    conn.commit()
    return cursor.rowcount > 0


# Generation CRUD
def create_generation(user_id: str, product_info: Dict[str, Any], 
                     attributes: Dict[str, Any], generated_contents: List[Dict[str, Any]]) -> Generation:
    """문구 생성 기록 저장"""
    conn = db.sqlite_conn
    generate_id = str(uuid.uuid4())
    now = datetime.now()
    
    import json
    conn.execute("""
        INSERT INTO generations (generate_id, user_id, product_info, attributes, generated_contents, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (generate_id, user_id, json.dumps(product_info, ensure_ascii=False),
          json.dumps(attributes, ensure_ascii=False),
          json.dumps(generated_contents, ensure_ascii=False), now))
    
    conn.commit()
    return Generation(
        generate_id=generate_id,
        user_id=user_id,
        product_info=product_info,
        attributes=attributes,
        generated_contents=generated_contents,
        created_at=now
    )


def get_generation(generate_id: str) -> Optional[Generation]:
    """문구 생성 기록 조회"""
    conn = db.sqlite_conn
    row = conn.execute("SELECT * FROM generations WHERE generate_id = ?", (generate_id,)).fetchone()
    
    if row:
        import json
        return Generation(
            generate_id=row['generate_id'],
            user_id=row['user_id'],
            product_info=json.loads(row['product_info']),
            attributes=json.loads(row['attributes']),
            generated_contents=json.loads(row['generated_contents']),
            created_at=datetime.fromisoformat(row['created_at'])
        )
    return None


def get_user_generations(user_id: str, limit: int = 10) -> List[Generation]:
    """사용자의 문구 생성 기록 조회"""
    conn = db.sqlite_conn
    rows = conn.execute("""
        SELECT * FROM generations 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit)).fetchall()
    
    import json
    return [Generation(
        generate_id=row['generate_id'],
        user_id=row['user_id'],
        product_info=json.loads(row['product_info']),
        attributes=json.loads(row['attributes']),
        generated_contents=json.loads(row['generated_contents']),
        created_at=datetime.fromisoformat(row['created_at'])
    ) for row in rows]


# Copy Action CRUD
def create_copy_action(user_id: str, generate_id: str, version_id: str, action_type: str = "copy") -> CopyAction:
    """복사 액션 로그 저장"""
    conn = db.sqlite_conn
    action_id = str(uuid.uuid4())
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO copy_actions (action_id, user_id, generate_id, version_id, action_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (action_id, user_id, generate_id, version_id, action_type, now))
    
    conn.commit()
    return CopyAction(
        action_id=action_id,
        user_id=user_id,
        generate_id=generate_id,
        version_id=version_id,
        action_type=action_type,
        created_at=now
    )


# Feedback CRUD
def create_feedback(user_id: str, feedback_text: str) -> Feedback:
    """피드백 저장"""
    conn = db.sqlite_conn
    feedback_id = str(uuid.uuid4())
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO feedbacks (feedback_id, user_id, feedback_text, created_at)
        VALUES (?, ?, ?, ?)
    """, (feedback_id, user_id, feedback_text, now))
    
    conn.commit()
    return Feedback(
        feedback_id=feedback_id,
        user_id=user_id,
        feedback_text=feedback_text,
        created_at=now
    )


# Regenerate Log CRUD
def create_regenerate_log(user_id: str, generate_id: str, reason_text: str, 
                         new_contents: List[Dict[str, Any]]) -> RegenerateLog:
    """재생성 로그 저장"""
    conn = db.sqlite_conn
    regenerate_id = str(uuid.uuid4())
    now = datetime.now()
    
    import json
    conn.execute("""
        INSERT INTO regenerate_logs (regenerate_id, user_id, generate_id, reason_text, new_contents, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (regenerate_id, user_id, generate_id, reason_text,
          json.dumps(new_contents, ensure_ascii=False), now))
    
    conn.commit()
    return RegenerateLog(
        regenerate_id=regenerate_id,
        user_id=user_id,
        generate_id=generate_id,
        reason_text=reason_text,
        new_contents=new_contents,
        created_at=now
    )
