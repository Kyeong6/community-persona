"""
커뮤니티 바이럴 콘텐츠 생성 시스템 - 모듈화된 구조
API 명세서 기반으로 역할별 모듈화 완료
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from database import init_database  # 임시 주석처리
from frontend import (
    show_user_info, show_content_history, 
    show_user_login_screen, show_input_form, show_results_screen
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
</style>
""", unsafe_allow_html=True)

# 데이터베이스 초기화 (임시 주석처리)
# init_database()

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
if 'current_generate_id' not in st.session_state:
    st.session_state.current_generate_id = None


# 로그인 화면은 streamlit.pages.login 모듈로 이동


def show_main_screen():
    """메인 화면"""
    # 사용자 정보 표시
    show_user_info(st.session_state.team_name, st.session_state.user_name, st.session_state.user_id)
    
    # 콘텐츠 이력 표시
    show_content_history(st.session_state.user_id)
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>✨ 커뮤 popular 콘텐츠 생성 시스템</h1>
        <p>상품 정보를 입력하고 커뮤니티에 맞는 원고를 자동으로 생성하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_results:
        show_input_form()
    else:
        show_results_screen()


# 입력 폼은 streamlit.pages.user_input 모듈로 이동


# 결과 화면은 streamlit.pages.copy_result 모듈로 이동


def main():
    """메인 함수"""
    # 사용자 로그인 확인
    if not st.session_state.user_logged_in:
        show_user_login_screen()
        return
    
    show_main_screen()


if __name__ == "__main__":
    main()
