"""
데이터베이스 연결 관리
SQLite와 ChromaDB 연결 설정
"""

import sqlite3
import chromadb
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings


class DatabaseConnection:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self, db_path: str = None, chroma_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.chroma_path = chroma_path or settings.CHROMA_PATH
        self._sqlite_conn = None
        self._chroma_client = None
        
        # 데이터 디렉토리 생성
        if not os.path.exists(settings.DATABASE_DIR):
            os.makedirs(settings.DATABASE_DIR)
        Path(self.chroma_path).mkdir(parents=True, exist_ok=True)
    
    @property
    def sqlite_conn(self):
        """SQLite 연결 반환"""
        if self._sqlite_conn is None:
            self._sqlite_conn = sqlite3.connect(self.db_path)
            self._sqlite_conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return self._sqlite_conn
    
    @property
    def chroma_client(self):
        """ChromaDB 클라이언트 반환"""
        if self._chroma_client is None:
            self._chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        return self._chroma_client
    
    def close(self):
        """연결 종료"""
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Database:
    """개선된 데이터베이스 클래스"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.connection = None
    
    def connect(self):
        """연결"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        """연결 종료"""
        if self.connection:
            self.connection.close()
    
    def execute(self, query, params=None):
        """쿼리 실행"""
        with self.connection:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
    
    def fetchall(self, query, params=None):
        """모든 행 조회"""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def fetchone(self, query, params=None):
        """단일 행 조회"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def commit(self):
        """커밋 수행"""
        if self.connection:
            self.connection.commit()


# 전역 데이터베이스 연결 인스턴스
db = DatabaseConnection()
