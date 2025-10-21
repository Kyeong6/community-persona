"""
FAISS 벡터 데이터베이스 적재 스크립트
CSV 파일의 데이터를 FAISS 인덱스로 변환하여 저장

사용법:
    # 기본 실행
    python load_faiss_data.py
    
    # 다른 CSV 파일 사용
    python load_faiss_data.py --csv my_data.csv
    
    # IVF 인덱스 타입 사용 (빠른 근사 검색)
    python load_faiss_data.py --index-type ivf
    
    # 검색 테스트 건너뛰기
    python load_faiss_data.py --no-test
    
    # 테스트 쿼리 수 조정
    python load_faiss_data.py --test-queries 5

필요한 컬럼:
    - id: int (고유 식별자)
    - channel: str (채널명)
    - category: str (카테고리)
    - title: str (제목)
    - content: str (내용)
    - view_cnt: int (조회수)
    - like_cnt: int (좋아요 수)
    - comment_cnt: int (댓글 수)
    - created_at: datetime (생성일시)
    - vector_title: str (제목 임베딩 벡터, 예: "[0.1, 0.2, 0.3, ...]")
    - vector_content: str (내용 임베딩 벡터, 예: "[0.1, 0.2, 0.3, ...]")

의존성 설치:
    poetry install --no-root

출력 파일:
    - data/faiss_indices/title_index_YYYYMMDD_HHMMSS.faiss (제목 벡터 인덱스)
    - data/faiss_indices/content_index_YYYYMMDD_HHMMSS.faiss (내용 벡터 인덱스)
    - data/faiss_indices/metadata_YYYYMMDD_HHMMSS.pkl (메타데이터)
    - data/faiss_indices/config_YYYYMMDD_HHMMSS.json (설정 정보)
"""

import pandas as pd
import numpy as np
import faiss
import pickle
import json
from datetime import datetime
import os
import sys
from pathlib import Path
import argparse

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_DIR = DATA_DIR / "faiss_indices"

# 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

def load_csv_data(csv_path):
    """CSV 파일 로드 및 전처리"""
    print(f"📁 CSV 파일 로드 중: {csv_path}")
    
    try:
        # CSV 파일 읽기
        df = pd.read_csv(csv_path)
        print(f"✅ 데이터 로드 완료: {len(df)}개 행")
        
        # 컬럼 확인
        expected_columns = [
            'id', 'channel', 'category', 'title', 'content', 
            'view_cnt', 'like_cnt', 'comment_cnt', 'created_at',
            'vector_title', 'vector_content'
        ]
        
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ 누락된 컬럼: {missing_columns}")
            return None
            
        print(f"📊 데이터 정보:")
        print(f"   - 총 행 수: {len(df)}")
        print(f"   - 컬럼 수: {len(df.columns)}")
        print(f"   - 채널 종류: {df['channel'].nunique()}개")
        print(f"   - 카테고리 종류: {df['category'].nunique()}개")
        
        return df
        
    except Exception as e:
        print(f"❌ CSV 파일 로드 실패: {e}")
        return None

def parse_vector_string(vector_str):
    """벡터 문자열을 numpy 배열로 변환"""
    try:
        if pd.isna(vector_str) or vector_str == '':
            return None
            
        # 문자열을 리스트로 변환
        if isinstance(vector_str, str):
            # 대괄호 제거 및 쉼표로 분리
            vector_str = vector_str.strip('[]')
            vector_list = [float(x.strip()) for x in vector_str.split(',')]
            return np.array(vector_list, dtype=np.float32)
        else:
            return None
            
    except Exception as e:
        print(f"⚠️ 벡터 파싱 실패: {e}")
        return None

def create_faiss_indexes(df, index_type='flat'):
    """FAISS 인덱스 생성"""
    print("🔧 FAISS 인덱스 생성 중...")
    
    # 벡터 데이터 추출 및 전처리
    title_vectors = []
    content_vectors = []
    metadata = []
    
    valid_indices = []
    skipped_count = 0
    
    for idx, row in df.iterrows():
        # 벡터 파싱
        title_vector = parse_vector_string(row['vector_title'])
        content_vector = parse_vector_string(row['vector_content'])
        
        if title_vector is not None and content_vector is not None:
            title_vectors.append(title_vector)
            content_vectors.append(content_vector)
            
            # 메타데이터 저장
            metadata.append({
                'id': int(row['id']),
                'channel': str(row['channel']),
                'category': str(row['category']),
                'title': str(row['title']),
                'content': str(row['content']),
                'view_cnt': int(row['view_cnt']) if pd.notna(row['view_cnt']) else 0,
                'like_cnt': int(row['like_cnt']) if pd.notna(row['like_cnt']) else 0,
                'comment_cnt': int(row['comment_cnt']) if pd.notna(row['comment_cnt']) else 0,
                'created_at': str(row['created_at']),
                'original_index': idx
            })
            
            valid_indices.append(idx)
        else:
            skipped_count += 1
            if skipped_count <= 5:  # 처음 5개만 출력
                print(f"⚠️ 행 {idx} 벡터 데이터 누락, 건너뜀")
    
    if skipped_count > 5:
        print(f"⚠️ 총 {skipped_count}개 행의 벡터 데이터가 누락되어 건너뜀")
    
    if not title_vectors:
        print("❌ 유효한 벡터 데이터가 없습니다.")
        return None, None, None
    
    # numpy 배열로 변환
    title_vectors = np.array(title_vectors)
    content_vectors = np.array(content_vectors)
    
    print(f"✅ 벡터 데이터 준비 완료:")
    print(f"   - 유효한 데이터: {len(title_vectors)}개")
    print(f"   - 제목 벡터 차원: {title_vectors.shape[1]}")
    print(f"   - 내용 벡터 차원: {content_vectors.shape[1]}")
    
    # FAISS 인덱스 생성
    title_index = create_optimized_index(title_vectors, index_type)
    content_index = create_optimized_index(content_vectors, index_type)
    
    print(f"✅ FAISS 인덱스 생성 완료:")
    print(f"   - 제목 인덱스 크기: {title_index.ntotal}")
    print(f"   - 내용 인덱스 크기: {content_index.ntotal}")
    
    return title_index, content_index, metadata

def save_indices_and_metadata(title_index, content_index, metadata):
    """인덱스와 메타데이터 저장"""
    print("💾 인덱스 및 메타데이터 저장 중...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # FAISS 인덱스 저장
    title_index_path = INDEX_DIR / f"title_index_{timestamp}.faiss"
    content_index_path = INDEX_DIR / f"content_index_{timestamp}.faiss"
    
    faiss.write_index(title_index, str(title_index_path))
    faiss.write_index(content_index, str(content_index_path))
    
    # 메타데이터 저장
    metadata_path = INDEX_DIR / f"metadata_{timestamp}.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    # 설정 정보 저장
    config = {
        'timestamp': timestamp,
        'total_records': len(metadata),
        'title_vector_dim': title_index.d,
        'content_vector_dim': content_index.d,
        'index_type': type(title_index).__name__,
        'created_at': datetime.now().isoformat(),
        'description': 'FAISS 벡터 데이터베이스 인덱스'
    }
    
    config_path = INDEX_DIR / f"config_{timestamp}.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 저장 완료:")
    print(f"   - 제목 인덱스: {title_index_path}")
    print(f"   - 내용 인덱스: {content_index_path}")
    print(f"   - 메타데이터: {metadata_path}")
    print(f"   - 설정 파일: {config_path}")
    
    return {
        'title_index_path': str(title_index_path),
        'content_index_path': str(content_index_path),
        'metadata_path': str(metadata_path),
        'config_path': str(config_path),
        'timestamp': timestamp
    }

def test_index_search(title_index, content_index, metadata, test_queries=3):
    """인덱스 검색 테스트"""
    print("🔍 인덱스 검색 테스트 중...")
    
    for i in range(min(test_queries, len(metadata))):
        # 테스트용 쿼리 벡터 (첫 번째 벡터 사용)
        title_query = title_index.reconstruct(i).reshape(1, -1)
        content_query = content_index.reconstruct(i).reshape(1, -1)
        
        # 검색 실행
        title_distances, title_indices = title_index.search(title_query, k=5)
        content_distances, content_indices = content_index.search(content_query, k=5)
        
        print(f"\n📋 테스트 {i+1}:")
        print(f"   원본 제목: {metadata[i]['title'][:50]}...")
        print(f"   원본 내용: {metadata[i]['content'][:50]}...")
        
        print(f"   제목 유사도 검색 결과:")
        for j, (dist, idx) in enumerate(zip(title_distances[0], title_indices[0])):
            print(f"     {j+1}. 거리: {dist:.4f}, 제목: {metadata[idx]['title'][:30]}...")
        
        print(f"   내용 유사도 검색 결과:")
        for j, (dist, idx) in enumerate(zip(content_distances[0], content_indices[0])):
            print(f"     {j+1}. 거리: {dist:.4f}, 내용: {metadata[idx]['content'][:30]}...")

def validate_csv_structure(df):
    """CSV 구조 검증"""
    print("🔍 CSV 구조 검증 중...")
    
    required_columns = [
        'id', 'channel', 'category', 'title', 'content', 
        'view_cnt', 'like_cnt', 'comment_cnt', 'created_at',
        'vector_title', 'vector_content'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ 누락된 필수 컬럼: {missing_columns}")
        return False
    
    # 데이터 타입 검증
    try:
        # 숫자형 컬럼 검증
        numeric_columns = ['id', 'view_cnt', 'like_cnt', 'comment_cnt']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 벡터 컬럼 검증
        vector_columns = ['vector_title', 'vector_content']
        for col in vector_columns:
            if df[col].isna().all():
                print(f"❌ {col} 컬럼에 유효한 데이터가 없습니다.")
                return False
        
        print("✅ CSV 구조 검증 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 타입 검증 실패: {e}")
        return False

def create_optimized_index(vectors, index_type='flat'):
    """최적화된 FAISS 인덱스 생성"""
    print(f"🔧 {index_type} 타입 인덱스 생성 중...")
    
    if index_type == 'flat':
        # L2 거리 기반 평면 인덱스 (정확한 검색)
        index = faiss.IndexFlatL2(vectors.shape[1])
    elif index_type == 'ivf':
        # IVF 인덱스 (빠른 근사 검색)
        quantizer = faiss.IndexFlatL2(vectors.shape[1])
        index = faiss.IndexIVFFlat(quantizer, vectors.shape[1], min(100, len(vectors)))
        index.train(vectors)
    else:
        raise ValueError(f"지원하지 않는 인덱스 타입: {index_type}")
    
    index.add(vectors)
    return index

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='FAISS 벡터 데이터베이스 적재 스크립트')
    parser.add_argument('--csv', type=str, default='community_data.csv', 
                       help='CSV 파일 경로 (기본값: community_data.csv)')
    parser.add_argument('--index-type', type=str, default='flat', 
                       choices=['flat', 'ivf'], help='FAISS 인덱스 타입 (기본값: flat)')
    parser.add_argument('--test-queries', type=int, default=3, 
                       help='검색 테스트 쿼리 수 (기본값: 3)')
    parser.add_argument('--no-test', action='store_true', 
                       help='검색 테스트 건너뛰기')
    
    args = parser.parse_args()
    
    print("🚀 FAISS 벡터 데이터베이스 적재 스크립트")
    print("=" * 50)
    print(f"📁 CSV 파일: {args.csv}")
    print(f"🔧 인덱스 타입: {args.index_type}")
    print(f"🔍 테스트 쿼리: {args.test_queries}")
    print()
    
    # CSV 파일 경로
    csv_path = PROJECT_ROOT / args.csv
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        print("💡 사용 가능한 CSV 파일을 확인하세요.")
        return 1
    
    try:
        # 1. CSV 데이터 로드
        df = load_csv_data(csv_path)
        if df is None:
            return 1
        
        # 2. CSV 구조 검증
        if not validate_csv_structure(df):
            return 1
        
        # 3. FAISS 인덱스 생성
        title_index, content_index, metadata = create_faiss_indexes(df, args.index_type)
        if title_index is None:
            return 1
        
        # 4. 인덱스 및 메타데이터 저장
        save_info = save_indices_and_metadata(title_index, content_index, metadata)
        
        # 5. 검색 테스트 (옵션)
        if not args.no_test:
            test_index_search(title_index, content_index, metadata, args.test_queries)
        
        print("\n🎉 FAISS 벡터 데이터베이스 적재 완료!")
        print(f"📁 인덱스 파일들이 {INDEX_DIR}에 저장되었습니다.")
        
        # 최신 인덱스 정보 출력
        print(f"\n📋 생성된 인덱스 정보:")
        print(f"   - 타임스탬프: {save_info['timestamp']}")
        print(f"   - 총 레코드 수: {len(metadata)}")
        print(f"   - 제목 벡터 차원: {title_index.d}")
        print(f"   - 내용 벡터 차원: {content_index.d}")
        print(f"   - 인덱스 타입: {args.index_type}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

