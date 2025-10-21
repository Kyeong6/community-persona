import os
import sys
import random
import streamlit as st
import pandas as pd
from datetime import datetime, date

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Frontend 모듈 import
from frontend import (
    show_user_login_screen, 
    show_input_form, 
    show_results_screen,
    show_user_info, 
    show_content_history
)

# 페이지 설정
st.set_page_config(
    page_title="커뮤니티 바이럴 콘텐츠 생성 시스템",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .emphasis-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
    }
    
    .emphasis-badge.selected {
        background: #1976d2;
        color: white;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'team_name' not in st.session_state:
    st.session_state.team_name = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'generated_contents' not in st.session_state:
    st.session_state.generated_contents = []
if 'selected_emphasis' not in st.session_state:
    st.session_state.selected_emphasis = []
if 'emphasis_details' not in st.session_state:
    st.session_state.emphasis_details = []
if 'content_history' not in st.session_state:
    st.session_state.content_history = []

def handle_user_login(team_name: str, user_name: str):
    """사용자 식별 및 등록 함수"""
    import hashlib
    import time
    
    # 고유 user_id 생성 (팀명 + 사용자명 + 타임스탬프 기반)
    timestamp = str(int(time.time()))
    user_string = f"{team_name}_{user_name}_{timestamp}"
    user_id = hashlib.md5(user_string.encode()).hexdigest()[:12]
    
    # 세션 상태 업데이트
    st.session_state.user_id = user_id
    st.session_state.team_name = team_name
    st.session_state.user_name = user_name
    st.session_state.user_logged_in = True
    
    return user_id

def generate_content(product_name, price, start_date, end_date, community, emphasis_details, best_case=""):
    """원고 생성 함수 (임시 - 하드코딩된 예시)"""
    
    # 커뮤니티별 톤 조정
    community_tones = {
        'ppomppu': ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'],
        'fmkorea': ['정보 전달형', '후기형', '친근한 톤', '유머러스한 톤'],
        'womad': ['후기형', '친근한 톤', '정보 전달형', '유머러스한 톤']
    }
    
    tones = community_tones.get(community, ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'])
    
    # 강조사항 텍스트 생성
    emphasis_text = '\n'.join([f"• {detail}" for detail in emphasis_details]) if emphasis_details else ""
    
    # 날짜 포맷팅
    start_str = start_date.strftime('%m월 %d일') if start_date else ""
    end_str = end_date.strftime('%m월 %d일') if end_date else ""
    
    # 커뮤니티명 변환
    community_names = {
        'ppomppu': '뽐뿌',
        'fmkorea': '에펨코리아', 
        'womad': '여성시대'
    }
    community_name = community_names.get(community, community)
    
    # 각 톤별 원고 생성
    contents = []
    
    # 1. 친근한 톤
    contents.append({
        'id': 1,
        'tone': '친근한 톤',
        'text': f"""{product_name} 이거 진짜 대박이에요 ㄷㄷ

작년에 {price}에 샀는데 지금 보니까 또 세일하네요.
이 가격에 이 퀄리티면 가성비 ㅇㅈ?

{emphasis_text}

놓치면 후회할 듯... 저는 재구매 각입니다 👍"""
    })
    
    # 2. 정보 전달형
    contents.append({
        'id': 2,
        'tone': '정보 전달형',
        'text': f"""{product_name} 특가 정보 공유합니다.

가격: {price}
기간: {start_str} ~ {end_str}

{emphasis_text}

비교해보니 역대급 가격인 것 같아서 올립니다.
필요하신 분들 참고하세요!"""
    })
    
    # 3. 후기형
    contents.append({
        'id': 3,
        'tone': '후기형',
        'text': f"""{product_name} 쓴지 3개월 됐는데 후기 남깁니다.

솔직히 처음엔 {price} 주고 사기 좀 망설였는데
지금은 완전 만족 중이에요 ㅎㅎ

{emphasis_text}

지금 또 세일한다길래 주변에 추천하려고 글 올려요.
고민하시는 분들한테는 강추!"""
    })
    
    # 4. 유머러스한 톤
    contents.append({
        'id': 4,
        'tone': '유머러스한 톤',
        'text': f"""{product_name} {price}이라니...

(이거 사야되나 말아야되나 고민중)

{emphasis_text}

지갑: 안돼...😭
나: 어차피 살 거 지금 사는 게 이득 아니야?
지갑: ...💸

결국 또 질렀습니다 여러분 ㅋㅋㅋ
같이 망하실 분? 🙋‍♀️"""
    })
    
    return contents

def main():
    # 사용자 로그인 확인
    if not st.session_state.user_logged_in:
        show_user_login_screen()
        return
    
    # 로그인된 사용자 정보 표시
    show_user_info(st.session_state.team_name, st.session_state.user_name, st.session_state.user_id)
    
    # 콘텐츠 이력 표시
    show_content_history(st.session_state.user_id)
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>✨ 커뮤니티 바이럴 콘텐츠 생성 시스템</h1>
        <p>상품 정보를 입력하고 커뮤니티에 맞는 원고를 자동으로 생성하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_results:
        show_input_form()
    else:
        show_results_screen()

if __name__ == "__main__":
    main()
