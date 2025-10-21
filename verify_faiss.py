#!/usr/bin/env python3
"""
FAISS 인덱스 검증 스크립트
메타데이터와 벡터 값이 제대로 저장되었는지 확인
"""

import faiss
import pickle
import json
import numpy as np
from pathlib import Path
import sys

def verify_faiss_indices():
    """FAISS 인덱스 검증"""
    
    PROJECT_ROOT = Path(__file__).parent
    INDICES_DIR = PROJECT_ROOT / "data" / "faiss_indices"
    
    print("🔍 FAISS 인덱스 검증 중...")
    print(f"📁 인덱스 디렉토리: {INDICES_DIR}")
    
    # 최신 인덱스 파일 찾기
    config_files = list(INDICES_DIR.glob("config_*.json"))
    if not config_files:
        print("❌ 설정 파일을 찾을 수 없습니다.")
        return False
    
    # 가장 최신 파일 선택
    latest_config = max(config_files, key=lambda x: x.stat().st_mtime)
    timestamp = latest_config.stem.replace("config_", "")
    
    print(f"📋 검증할 인덱스: {timestamp}")
    
    # 파일 경로 설정
    title_index_path = INDICES_DIR / f"title_index_{timestamp}.faiss"
    content_index_path = INDICES_DIR / f"content_index_{timestamp}.faiss"
    metadata_path = INDICES_DIR / f"metadata_{timestamp}.pkl"
    config_path = INDICES_DIR / f"config_{timestamp}.json"
    
    # 파일 존재 확인
    files_to_check = [title_index_path, content_index_path, metadata_path, config_path]
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return False
    
    print("✅ 모든 파일이 존재합니다.")
    
    # 설정 파일 로드
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"\n📊 설정 정보:")
    print(f"   - 총 레코드 수: {config['total_records']}")
    print(f"   - 제목 벡터 차원: {config['title_vector_dim']}")
    print(f"   - 내용 벡터 차원: {config['content_vector_dim']}")
    print(f"   - 인덱스 타입: {config['index_type']}")
    print(f"   - 생성 시간: {config['created_at']}")
    
    # FAISS 인덱스 로드
    print(f"\n🔧 FAISS 인덱스 로드 중...")
    title_index = faiss.read_index(str(title_index_path))
    content_index = faiss.read_index(str(content_index_path))
    
    print(f"✅ 인덱스 로드 완료:")
    print(f"   - 제목 인덱스 크기: {title_index.ntotal}")
    print(f"   - 내용 인덱스 크기: {content_index.ntotal}")
    print(f"   - 제목 벡터 차원: {title_index.d}")
    print(f"   - 내용 벡터 차원: {content_index.d}")
    
    # 메타데이터 로드
    print(f"\n📋 메타데이터 로드 중...")
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    print(f"✅ 메타데이터 로드 완료: {len(metadata)}개 레코드")
    
    # 메타데이터 샘플 확인
    print(f"\n📝 메타데이터 샘플 (첫 3개):")
    for i, meta in enumerate(metadata[:3]):
        print(f"   {i+1}. ID: {meta['id']}")
        print(f"      채널: {meta['channel']}")
        print(f"      카테고리: {meta['category']}")
        print(f"      제목: {meta['title'][:50]}...")
        print(f"      내용: {meta['content'][:50]}...")
        print(f"      조회수: {meta['view_cnt']}")
        print(f"      좋아요: {meta['like_cnt']}")
        print(f"      댓글: {meta['comment_cnt']}")
        print(f"      생성일: {meta['created_at']}")
        print()
    
    # 벡터 값 검증
    print(f"🔍 벡터 값 검증 중...")
    
    # 첫 번째 벡터 추출
    title_vector = title_index.reconstruct(0)
    content_vector = content_index.reconstruct(0)
    
    print(f"✅ 벡터 추출 완료:")
    print(f"   - 제목 벡터 차원: {len(title_vector)}")
    print(f"   - 내용 벡터 차원: {len(content_vector)}")
    print(f"   - 제목 벡터 샘플: {title_vector[:5]}...")
    print(f"   - 내용 벡터 샘플: {content_vector[:5]}...")
    
    # 벡터 통계
    print(f"\n📊 벡터 통계:")
    print(f"   - 제목 벡터 최솟값: {title_vector.min():.6f}")
    print(f"   - 제목 벡터 최댓값: {title_vector.max():.6f}")
    print(f"   - 제목 벡터 평균: {title_vector.mean():.6f}")
    print(f"   - 내용 벡터 최솟값: {content_vector.min():.6f}")
    print(f"   - 내용 벡터 최댓값: {content_vector.max():.6f}")
    print(f"   - 내용 벡터 평균: {content_vector.mean():.6f}")
    
    # 검색 테스트
    print(f"\n🔍 검색 테스트:")
    query_vector = title_vector.reshape(1, -1)
    distances, indices = title_index.search(query_vector, k=3)
    
    print(f"   검색 결과 (상위 3개):")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        print(f"     {i+1}. 거리: {dist:.6f}, 인덱스: {idx}")
        print(f"        제목: {metadata[idx]['title'][:40]}...")
    
    # 데이터 일관성 검증
    print(f"\n✅ 데이터 일관성 검증:")
    
    # 인덱스 크기와 메타데이터 크기 일치 확인
    if title_index.ntotal == len(metadata) and content_index.ntotal == len(metadata):
        print(f"   ✅ 인덱스 크기와 메타데이터 크기 일치: {len(metadata)}")
    else:
        print(f"   ❌ 크기 불일치: 인덱스({title_index.ntotal}, {content_index.ntotal}) vs 메타데이터({len(metadata)})")
        return False
    
    # 벡터 차원 확인
    if title_index.d == config['title_vector_dim'] and content_index.d == config['content_vector_dim']:
        print(f"   ✅ 벡터 차원 일치: 제목({title_index.d}), 내용({content_index.d})")
    else:
        print(f"   ❌ 벡터 차원 불일치")
        return False
    
    # 메타데이터 필드 확인
    required_fields = ['id', 'channel', 'category', 'title', 'content', 'view_cnt', 'like_cnt', 'comment_cnt', 'created_at']
    sample_meta = metadata[0]
    missing_fields = [field for field in required_fields if field not in sample_meta]
    
    if not missing_fields:
        print(f"   ✅ 메타데이터 필드 완전: {len(required_fields)}개 필드")
    else:
        print(f"   ❌ 누락된 메타데이터 필드: {missing_fields}")
        return False
    
    print(f"\n🎉 FAISS 인덱스 검증 완료!")
    print(f"   모든 데이터가 정상적으로 저장되었습니다.")
    
    return True

if __name__ == "__main__":
    success = verify_faiss_indices()
    sys.exit(0 if success else 1)
