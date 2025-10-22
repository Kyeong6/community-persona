import sqlite3
import os
from core.config import settings

# 데이터베이스(SQLite) 경로 : data/database/database.db

# 디렉토리 존재하지 않으면 생성 
if not os.path.exists(settings.DATABASE_DIR):
    os.makedirs(settings.DATABASE_DIR)

# 데이터베이스 연결 관리 정의
class Database:
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self.connection = None
    
    # 연결
    def connect(self):
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Database connection error: {e}")
            print(f"Trying to create database at: {self.db_path}")
            raise
    
    # 연결 종료
    def close(self):
        if self.connection:
            self.connection.close()
    
    # 쿼리 실행
    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    # 모든 행 조회
    def fetchall(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    # 단일 행 조회
    def fetchone(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    # 커밋 수행
    def commit(self):
        if self.connection:
            self.connection.commit()