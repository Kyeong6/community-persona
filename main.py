import streamlit as st
from database import create_tables

# 데이터베이스 초기화
create_tables()

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
    page_title="Community Viral Content Generator",
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
        background: linear-gradient(135deg, #667eea 0%, #4285f4 100%);
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
        <p>상품 정보를 입력하고 커뮤니티에 맞는 원고를 자동으로 생성하세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_results:
        show_input_form()
    else:
        show_results_screen()

if __name__ == "__main__":
    main()
