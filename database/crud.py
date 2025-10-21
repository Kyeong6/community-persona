import uuid
from datetime import datetime
from database.connection import Database

# 데이터베이스 테이블 생성
def create_tables():

    db = Database()
    db.connect()

    # 사용자 테이블
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY NOT NULL,
            team_name TEXT NOT NULL,
            user_name TEXT NOT NULL,
            created_at DATETIME NOT NULL
        )
    """)

    # 사용자 피드백 테이블
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id TEXT PRIMARY KEY NOT NULL,
            user_id TEXT NOT NULL,
            feedback TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 콘텐츠 생성 기록 테이블
    db.execute("""
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

    db.commit()
    db.close()


# 사용자 생성
def create_user(team_name: str, user_name: str, user_id: str):
    db = Database()
    db.connect()
    now = datetime.now()
    
    db.execute("""
        INSERT INTO users (id, team_name, user_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, team_name, user_name, now))
    
    db.commit()
    db.close()


# 사용자 조회
def get_user(user_id: str):
    db = Database()
    db.connect()
    row = db.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))
    db.close()
    
    if row:
        return {
            'id': row['id'],
            'team_name': row['team_name'],
            'user_name': row['user_name'],
            'created_at': row['created_at']
        }
    return None


# 사용자 피드백 생성
def create_user_feedback(user_id: str, feedback: str) -> str:
    db = Database()
    db.connect()
    feedback_id = str(uuid.uuid4())
    now = datetime.now()
    
    db.execute("""
        INSERT INTO user_feedback (id, user_id, feedback, created_at)
        VALUES (?, ?, ?, ?)
    """, (feedback_id, user_id, feedback, now))
    
    db.commit()
    db.close()
    
    return feedback_id


# 콘텐츠 생성 기록 저장
def create_content(user_id: str, parent_generate_id: str, generation_type: str, product_info: dict, 
                  attributes: dict, generated_contents: list, 
                  reason: str = None) -> str:
    db = Database()
    db.connect()
    content_id = str(uuid.uuid4())
    now = datetime.now()
    
    db.execute("""
        INSERT INTO contents (id, user_id, parent_generate_id, generation_type, 
                            product_info, attributes, generated_contents, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (content_id, user_id, parent_generate_id, generation_type,
          product_info, attributes, generated_contents,
          reason, now))
    
    db.commit()
    db.close()

    # 콘텐츠 ID 반환
    return content_id


# 콘텐츠 조회
def get_content(content_id: str):
    db = Database()
    db.connect()
    row = db.fetchone("SELECT * FROM contents WHERE id = ?", (content_id,))
    db.close()
    
    if row:
        return {
            'id': row['id'],
            'user_id': row['user_id'],
            'parent_generate_id': row['parent_generate_id'],
            'generation_type': row['generation_type'],
            'product_info': row['product_info'],
            'attributes': row['attributes'],
            'generated_contents': row['generated_contents'],
            'reason': row['reason'],
            'created_at': row['created_at']
        }
    # 콘텐츠 없으면 None 반환
    return None

# 사용자 콘텐츠 조회
def get_user_contents(user_id: str, limit: int = 10):
    db = Database()
    db.connect()
    rows = db.fetchall("""
        SELECT id, user_id, parent_generate_id, generation_type, product_info, attributes, generated_contents, reason, created_at FROM contents 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    db.close()
    
    return [{
        'id': row['id'],
        'user_id': row['user_id'],
        'parent_generate_id': row['parent_generate_id'],
        'generation_type': row['generation_type'],
        'product_info': row['product_info'],
        'attributes': row['attributes'],
        'generated_contents': row['generated_contents'],
        'reason': row['reason'],
        'created_at': row['created_at']
    } for row in rows]
    
    # 사용자 콘텐츠 없으면 빈 리스트 반환
    return []