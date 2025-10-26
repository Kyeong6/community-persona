import uuid
import json
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
            rating INTEGER DEFAULT 5,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 기존 테이블에 rating 컬럼 추가 (이미 존재하면 무시됨)
    try:
        db.execute("ALTER TABLE user_feedback ADD COLUMN rating INTEGER DEFAULT 5")
    except:
        # 컬럼이 이미 존재하는 경우 무시
        pass

    # 사용자 입력 정보 테이블
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_inputs (
            id TEXT PRIMARY KEY NOT NULL,
            user_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            price TEXT,
            product_attribute TEXT,
            event TEXT,
            card TEXT,
            coupon TEXT,
            keyword TEXT,
            etc TEXT,
            community TEXT NOT NULL,
            best_case TEXT,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 콘텐츠 생성 기록 테이블
    db.execute("""
        CREATE TABLE IF NOT EXISTS contents (
            id TEXT PRIMARY KEY NOT NULL,
            input_id TEXT NOT NULL,
            parent_generate_id TEXT,
            generation_type TEXT NOT NULL,
            product_info TEXT NOT NULL,
            attributes TEXT NOT NULL,
            generated_contents TEXT NOT NULL,
            reason TEXT,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (input_id) REFERENCES user_inputs(id)
        )
    """)

    # 채택 기록 테이블 (복사 버튼 클릭 추적)
    db.execute("""
        CREATE TABLE IF NOT EXISTS content_adoptions (
            id TEXT PRIMARY KEY NOT NULL,
            user_id TEXT NOT NULL,
            content_id TEXT NOT NULL,
            tone TEXT NOT NULL,
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

# 팀명과 사용자명으로 사용자 조회
def get_user_by_team_and_name(team_name: str, user_name: str):
    db = Database()
    db.connect()
    row = db.fetchone("SELECT * FROM users WHERE team_name = ? AND user_name = ?", (team_name, user_name))
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
def create_user_feedback(user_id: str, feedback: str, rating: int = 5) -> str:
    db = Database()
    db.connect()
    feedback_id = str(uuid.uuid4())
    now = datetime.now()
    
    db.execute("""
        INSERT INTO user_feedback (id, user_id, feedback, rating, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (feedback_id, user_id, feedback, rating, now))
    
    db.commit()
    db.close()
    
    return feedback_id


# 사용자 입력 정보 저장
def create_user_input(user_id: str, product_name: str, price: str = None, 
                     product_attribute: str = None, event: str = None, 
                     card: str = None, coupon: str = None, keyword: str = None, 
                     etc: str = None, community: str = None, best_case: str = None) -> str:
    db = Database()
    db.connect()
    input_id = str(uuid.uuid4())
    now = datetime.now()
    
    db.execute("""
        INSERT INTO user_inputs (id, user_id, product_name, price, product_attribute, 
                               event, card, coupon, keyword, etc, community, best_case, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (input_id, user_id, product_name, price, product_attribute, 
          event, card, coupon, keyword, etc, community, best_case, now))
    
    db.commit()
    db.close()
    
    return input_id


# 사용자 입력 정보 조회
def get_user_input(input_id: str):
    db = Database()
    db.connect()
    row = db.fetchone("SELECT * FROM user_inputs WHERE id = ?", (input_id,))
    db.close()
    
    if row:
        return {
            'id': row['id'],
            'user_id': row['user_id'],
            'product_name': row['product_name'],
            'price': row['price'],
            'product_attribute': row['product_attribute'],
            'event': row['event'],
            'card': row['card'],
            'coupon': row['coupon'],
            'keyword': row['keyword'],
            'etc': row['etc'],
            'community': row['community'],
            'best_case': row['best_case'],
            'created_at': row['created_at']
        }
    return None


# 사용자의 입력 기록 조회
def get_user_inputs(user_id: str, limit: int = 10):
    db = Database()
    db.connect()
    rows = db.fetchall("""
        SELECT id, user_id, product_name, price, product_attribute, event, card, 
               coupon, keyword, etc, community, best_case, created_at 
        FROM user_inputs 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    db.close()
    
    return [{
        'id': row['id'],
        'user_id': row['user_id'],
        'product_name': row['product_name'],
        'price': row['price'],
        'product_attribute': row['product_attribute'],
        'event': row['event'],
        'card': row['card'],
        'coupon': row['coupon'],
        'keyword': row['keyword'],
        'etc': row['etc'],
        'community': row['community'],
        'best_case': row['best_case'],
        'created_at': row['created_at']
    } for row in rows]


# 콘텐츠 생성 기록 저장
def create_content(input_id: str, parent_generate_id: str, generation_type: str, 
                  product_info: dict, attributes: dict, generated_contents: list, 
                  reason: str = None) -> str:
    db = Database()
    db.connect()
    content_id = str(uuid.uuid4())
    now = datetime.now()
    
    db.execute("""
        INSERT INTO contents (id, input_id, parent_generate_id, generation_type, 
                            product_info, attributes, generated_contents, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (content_id, input_id, parent_generate_id, generation_type,
          json.dumps(product_info, ensure_ascii=False),
          json.dumps(attributes, ensure_ascii=False),
          json.dumps(generated_contents, ensure_ascii=False),
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
            'input_id': row['input_id'],
            'parent_generate_id': row['parent_generate_id'],
            'generation_type': row['generation_type'],
            'product_info': json.loads(row['product_info']),
            'attributes': json.loads(row['attributes']),
            'generated_contents': json.loads(row['generated_contents']),
            'reason': row['reason'],
            'created_at': row['created_at']
        }
    # 콘텐츠 없으면 None 반환
    return None

# 사용자 콘텐츠 조회 (JOIN 사용)
def get_user_contents(user_id: str, limit: int = 10):
    db = Database()
    db.connect()
    rows = db.fetchall("""
        SELECT c.id, c.input_id, c.parent_generate_id, c.generation_type, 
               c.product_info, c.attributes, c.generated_contents, c.reason, c.created_at,
               ui.user_id, ui.product_name, ui.community
        FROM contents c
        JOIN user_inputs ui ON c.input_id = ui.id
        WHERE ui.user_id = ? 
        ORDER BY c.created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    db.close()
    
    return [{
        'id': row['id'],
        'input_id': row['input_id'],
        'user_id': row['user_id'],
        'product_name': row['product_name'],
        'community': row['community'],
        'parent_generate_id': row['parent_generate_id'],
        'generation_type': row['generation_type'],
        'product_info': json.loads(row['product_info']),
        'attributes': json.loads(row['attributes']),
        'generated_contents': json.loads(row['generated_contents']),
        'reason': row['reason'],
        'created_at': row['created_at']
    } for row in rows]
    
    # 사용자 콘텐츠 없으면 빈 리스트 반환
    return []

# 콘텐츠 수정
def update_content_text(content_id: str, version_id: int, new_text: str):
    """특정 콘텐츠의 특정 버전 텍스트를 수정"""
    db = Database()
    db.connect()
    
    # 기존 콘텐츠 조회
    content = get_content(content_id)
    if not content:
        db.close()
        return False
    
    # generated_contents 업데이트
    generated_contents = content['generated_contents']
    for content_item in generated_contents:
        if content_item['id'] == version_id:
            content_item['text'] = new_text
            break
    
    # 데이터베이스 업데이트
    db.execute("""
        UPDATE contents 
        SET generated_contents = ?
        WHERE id = ?
    """, (json.dumps(generated_contents, ensure_ascii=False), content_id))
    
    db.commit()
    db.close()
    return True

# 사용자 생성 히스토리 조회
def get_user_generations(user_id: str, limit: int = 10):
    """
    사용자의 생성 히스토리를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 최대 개수
    
    Returns:
        list: 생성 히스토리 리스트
    """
    db = Database()
    db.connect()
    
    try:
        cursor = db.execute("""
            SELECT c.id, c.product_info, c.attributes, c.generated_contents, c.created_at, c.generation_type
            FROM contents c
            JOIN user_inputs ui ON c.input_id = ui.id
            WHERE ui.user_id = ?
            ORDER BY c.created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        generations = []
        
        for row in results:
            generations.append({
                "id": row[0],
                "product_info": json.loads(row[1]) if row[1] else {},
                "attributes": json.loads(row[2]) if row[2] else {},
                "generated_contents": json.loads(row[3]) if row[3] else [],
                "created_at": row[4],
                "generation_type": row[5]
            })
        
        return generations
        
    except Exception as e:
        print(f"Error retrieving user generations: {e}")
        return []
    finally:
        db.close()

# 채택 기록 저장
def record_content_adoption(user_id: str, content_id: str, tone: str):
    """콘텐츠 채택 기록을 저장합니다."""
    db = Database()
    db.connect()
    
    adoption_id = str(uuid.uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db.execute("""
        INSERT INTO content_adoptions (id, user_id, content_id, tone, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (adoption_id, user_id, content_id, tone, now))
    
    db.commit()
    db.close()
    return adoption_id

# 사용자 채택 횟수 조회
def get_user_adoption_count(user_id: str):
    """사용자의 총 채택 횟수를 조회합니다."""
    db = Database()
    db.connect()
    
    try:
        cursor = db.execute("""
            SELECT COUNT(*) as adoption_count
            FROM content_adoptions
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error retrieving adoption count: {e}")
        return 0
    finally:
        db.close()

# 사용자 선호 톤 조회
def get_user_preferred_tone(user_id: str):
    """사용자가 가장 많이 채택한 톤을 조회합니다."""
    db = Database()
    db.connect()
    
    try:
        cursor = db.execute("""
            SELECT tone, COUNT(*) as count
            FROM content_adoptions
            WHERE user_id = ?
            GROUP BY tone
            ORDER BY count DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            return result[0]  # 가장 많이 채택한 톤
        return None
        
    except Exception as e:
        print(f"Error retrieving preferred tone: {e}")
        return None
    finally:
        db.close()

# 사용자 피드백 히스토리 조회
def get_user_feedbacks(user_id: str, limit: int = 10):
    """
    사용자의 피드백 히스토리를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        limit: 조회할 최대 개수
    
    Returns:
        list: 피드백 히스토리 리스트
    """
    db = Database()
    db.connect()
    
    try:
        cursor = db.execute("""
            SELECT id, feedback_text, feedback_type, created_at
            FROM user_feedback
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        feedbacks = []
        
        for row in results:
            feedbacks.append({
                "id": row[0],
                "feedback_text": row[1],
                "feedback_type": row[2],
                "created_at": row[3]
            })
        
        return feedbacks
        
    except Exception as e:
        print(f"Error retrieving user feedbacks: {e}")
        return []
    finally:
        db.close()