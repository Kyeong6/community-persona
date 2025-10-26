#!/usr/bin/env python3
"""
로그 파일 확인 스크립트
사용자 행동 패턴을 텍스트 파일로 확인할 수 있습니다.
"""

import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def parse_log_file(log_file_path="logs/info.log"):
    """로그 파일을 파싱하여 사용자 행동 데이터 추출"""
    if not os.path.exists(log_file_path):
        print(f"로그 파일을 찾을 수 없습니다: {log_file_path}")
        return []
    
    logs = []
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 사용자 행동 로그만 추출
            if any(action in line for action in ['COPY_ACTION', 'GENERATE_ACTION', 'EDIT_START', 'EDIT_COMPLETE', 'REGENERATE_ACTION', 'LOAD_FROM_HISTORY', 'BEST_CASE_APPLY', 'FEEDBACK_SUBMIT', 'FORM_RESET']):
                logs.append(line.strip())
    
    return logs

def analyze_logs(logs, days=7):
    """로그 분석"""
    if not logs:
        print("분석할 로그가 없습니다.")
        return
    
    # 최근 N일 필터링
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_logs = []
    
    for log in logs:
        try:
            # 로그에서 시간 추출 (형식: 2025-01-27 00:00:00)
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', log)
            if time_match:
                log_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                if log_time >= cutoff_date:
                    recent_logs.append(log)
        except:
            continue
    
    print(f"📊 최근 {days}일간 로그 분석 결과")
    print("=" * 50)
    print(f"총 로그 수: {len(recent_logs)}건")
    print()
    
    # 행동별 통계
    action_counts = Counter()
    user_actions = defaultdict(list)
    
    for log in recent_logs:
        # 행동 유형 추출
        if 'COPY_ACTION' in log:
            action_counts['복사'] += 1
        elif 'GENERATE_ACTION' in log:
            action_counts['생성'] += 1
        elif 'EDIT_START' in log:
            action_counts['수정시작'] += 1
        elif 'EDIT_COMPLETE' in log:
            action_counts['수정완료'] += 1
        elif 'REGENERATE_ACTION' in log:
            action_counts['재생성'] += 1
        elif 'LOAD_FROM_HISTORY' in log:
            action_counts['히스토리불러오기'] += 1
        elif 'BEST_CASE_APPLY' in log:
            action_counts['베스트사례적용'] += 1
        elif 'FEEDBACK_SUBMIT' in log:
            action_counts['피드백제출'] += 1
        elif 'FORM_RESET' in log:
            action_counts['폼초기화'] += 1
        
        # 사용자 ID 추출
        user_match = re.search(r'user_id: ([a-f0-9-]+)', log)
        if user_match:
            user_id = user_match.group(1)
            user_actions[user_id].append(log)
    
    # 행동별 통계 출력
    print("🎯 행동별 통계:")
    for action, count in action_counts.most_common():
        print(f"  {action}: {count}건")
    print()
    
    # 사용자별 통계
    print("👥 활성 사용자 통계:")
    print(f"  총 사용자 수: {len(user_actions)}명")
    
    # 상위 5명 사용자
    top_users = sorted(user_actions.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for i, (user_id, actions) in enumerate(top_users, 1):
        print(f"  {i}. 사용자 {user_id[:8]}...: {len(actions)}건")
    print()
    
    # 복사 행동 상세 분석
    copy_logs = [log for log in recent_logs if 'COPY_ACTION' in log]
    if copy_logs:
        print("📋 복사 행동 상세 분석:")
        tone_counts = Counter()
        community_counts = Counter()
        
        for log in copy_logs:
            # 톤 추출
            tone_match = re.search(r'tone: ([^,]+)', log)
            if tone_match:
                tone = tone_match.group(1).strip()
                tone_counts[tone] += 1
            
            # 커뮤니티 추출
            community_match = re.search(r'community: ([^,]+)', log)
            if community_match:
                community = community_match.group(1).strip()
                community_counts[community] += 1
        
        print("  인기 톤 Top 3:")
        for tone, count in tone_counts.most_common(3):
            print(f"    {tone}: {count}회")
        
        print("  커뮤니티별 복사:")
        for community, count in community_counts.most_common():
            print(f"    {community}: {count}회")
        print()
    
    # 생성 행동 상세 분석
    generate_logs = [log for log in recent_logs if 'GENERATE_ACTION' in log]
    if generate_logs:
        print("✨ 생성 행동 상세 분석:")
        community_gen_counts = Counter()
        
        for log in generate_logs:
            community_match = re.search(r'community: ([^,]+)', log)
            if community_match:
                community = community_match.group(1).strip()
                community_gen_counts[community] += 1
        
        print("  커뮤니티별 생성:")
        for community, count in community_gen_counts.most_common():
            print(f"    {community}: {count}건")
        print()
    
    # 피드백 분석
    feedback_logs = [log for log in recent_logs if 'FEEDBACK_SUBMIT' in log]
    if feedback_logs:
        print("💬 피드백 분석:")
        rating_counts = Counter()
        text_feedback_count = 0
        
        for log in feedback_logs:
            rating_match = re.search(r'rating: (\d+)', log)
            if rating_match:
                rating = int(rating_match.group(1))
                rating_counts[rating] += 1
            
            if 'has_feedback_text: True' in log:
                text_feedback_count += 1
        
        print(f"  총 피드백 수: {len(feedback_logs)}건")
        print(f"  텍스트 피드백: {text_feedback_count}건 ({text_feedback_count/len(feedback_logs)*100:.1f}%)")
        print("  별점 분포:")
        for rating in sorted(rating_counts.keys()):
            print(f"    {rating}점: {rating_counts[rating]}건")
        print()

def show_recent_logs(logs, count=20):
    """최근 로그 표시"""
    print(f"📝 최근 {count}개 로그:")
    print("=" * 50)
    
    for i, log in enumerate(logs[-count:], 1):
        print(f"{i:2d}. {log}")
    
    print()

def main():
    """메인 함수"""
    print("🔍 사용자 행동 로그 분석기")
    print("=" * 50)
    
    # 로그 파일 경로
    log_file = "logs/info.log"
    
    # 로그 파싱
    logs = parse_log_file(log_file)
    
    if not logs:
        print("로그 데이터가 없습니다.")
        return
    
    print(f"총 로그 수: {len(logs)}건")
    print()
    
    # 분석 기간 선택
    print("분석 기간을 선택하세요:")
    print("1. 1일")
    print("2. 3일")
    print("3. 7일 (기본)")
    print("4. 14일")
    print("5. 30일")
    print("6. 전체")
    
    choice = input("선택 (1-6, 기본값: 3): ").strip()
    
    if choice == "1":
        days = 1
    elif choice == "2":
        days = 3
    elif choice == "4":
        days = 14
    elif choice == "5":
        days = 30
    elif choice == "6":
        days = 9999  # 전체
    else:
        days = 7  # 기본값
    
    print()
    
    # 로그 분석
    analyze_logs(logs, days)
    
    # 최근 로그 표시 여부
    show_recent = input("최근 로그를 표시하시겠습니까? (y/N): ").strip().lower()
    if show_recent == 'y':
        show_recent_logs(logs)

if __name__ == "__main__":
    main()
