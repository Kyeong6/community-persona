"""
데이터베이스 연결 관리
SQLite와 FAISS 벡터 데이터베이스 연결 설정
"""

import sqlite3
import faiss
import numpy as np
import pickle
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings


class VectorDatabase:
    """FAISS 벡터 데이터베이스 클래스"""
    
    def __init__(self, vector_path: str = None, dimension: int = 384):
        self.vector_path = vector_path or settings.CHROMA_PATH
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self.ids = []
        
        # 벡터 디렉토리 생성
        Path(self.vector_path).mkdir(parents=True, exist_ok=True)
        
        # 기존 인덱스 로드 시도
        self._load_index()
    
    def _load_index(self):
        """기존 인덱스 로드"""
        index_path = os.path.join(self.vector_path, "faiss_index.bin")
        metadata_path = os.path.join(self.vector_path, "metadata.pkl")
        
        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                self.ids = [meta.get('id', f"doc_{i}") for i, meta in enumerate(self.metadata)]
                print(f"✅ FAISS 인덱스 로드 완료: {len(self.ids)}개 문서")
            except Exception as e:
                print(f"⚠️ 인덱스 로드 실패, 새로 생성: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """새 인덱스 생성"""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (코사인 유사도용)
        self.metadata = []
        self.ids = []
        print(f"✅ 새로운 FAISS 인덱스 생성: {self.dimension}차원")
    
    def add_vectors(self, vectors: np.ndarray, metadata_list: list, ids: list = None):
        """벡터와 메타데이터 추가"""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"벡터 차원이 맞지 않습니다: {vectors.shape[1]} != {self.dimension}")
        
        # 벡터 정규화 (코사인 유사도용)
        faiss.normalize_L2(vectors)
        
        # 인덱스에 추가
        self.index.add(vectors)
        
        # 메타데이터와 ID 저장
        self.metadata.extend(metadata_list)
        if ids:
            self.ids.extend(ids)
        else:
            start_id = len(self.ids)
            self.ids.extend([f"doc_{start_id + i}" for i in range(len(vectors))])
        
        print(f"✅ {len(vectors)}개 벡터 추가 완료")
    
    def search(self, query_vector: np.ndarray, k: int = 5):
        """벡터 검색"""
        if self.index.ntotal == 0:
            return [], []
        
        # 쿼리 벡터 정규화
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # 검색 수행
        scores, indices = self.index.search(query_vector, k)
        
        # 결과 반환
        results = []
        result_metadata = []
        
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # 유효한 결과만
                results.append(score)
                result_metadata.append(self.metadata[idx])
        
        return results, result_metadata
    
    def save(self):
        """인덱스와 메타데이터 저장"""
        index_path = os.path.join(self.vector_path, "faiss_index.bin")
        metadata_path = os.path.join(self.vector_path, "metadata.pkl")
        
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"✅ FAISS 인덱스 저장 완료: {index_path}")
    
    def get_stats(self):
        """인덱스 통계 정보"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata)
        }


class DatabaseConnection:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self, db_path: str = None, vector_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.vector_path = vector_path or settings.FAISS_INDICES_DIR
        self._sqlite_conn = None
        self._vector_db = None
        
        # 데이터 디렉토리 생성
        if not os.path.exists(settings.DATABASE_DIR):
            os.makedirs(settings.DATABASE_DIR)
        Path(self.vector_path).mkdir(parents=True, exist_ok=True)
    
    @property
    def sqlite_conn(self):
        """SQLite 연결 반환"""
        if self._sqlite_conn is None:
            self._sqlite_conn = sqlite3.connect(self.db_path)
            self._sqlite_conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return self._sqlite_conn
    
    @property
    def vector_db(self):
        """FAISS 벡터 데이터베이스 반환"""
        if self._vector_db is None:
            self._vector_db = VectorDatabase(self.vector_path)
        return self._vector_db
    
    def close(self):
        """연결 종료"""
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None
        if self._vector_db:
            self._vector_db.save()
    
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
