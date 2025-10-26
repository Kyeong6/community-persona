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
from frontend.components.sidebar import show_sidebar
from frontend.pages.history import show_history_page
from frontend.pages.community_cases import show_community_cases_page

# 페이지 설정
st.set_page_config(
    page_title="Community Viral Content Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    /* 사이드바 너비 확장 */
    .css-1d391kg {
        width: 350px !important;
    }
    
    /* 파랑색 버튼 스타일 - 새로운 원고 생성 버튼 */
    button[data-testid="baseButton-secondary"][aria-label*="새로운 원고 생성"] {
        background-color: #4285f4 !important;
        color: white !important;
        border: 1px solid #4285f4 !important;
    }
    
    button[data-testid="baseButton-secondary"][aria-label*="새로운 원고 생성"]:hover {
        background-color: #3367d6 !important;
        border-color: #3367d6 !important;
    }
    
    /* 대안: 키 기반 선택자 */
    button[data-testid="baseButton-secondary"][key="new_generation_btn"] {
        background-color: #4285f4 !important;
        color: white !important;
        border: 1px solid #4285f4 !important;
    }
    
    button[data-testid="baseButton-secondary"][key="new_generation_btn"]:hover {
        background-color: #3367d6 !important;
        border-color: #3367d6 !important;
    }
    
    /* 더 강력한 선택자 - 모든 secondary 버튼 중 마지막 */
    div[data-testid="column"]:last-child button[data-testid="baseButton-secondary"] {
        background-color: #4285f4 !important;
        color: white !important;
        border: 1px solid #4285f4 !important;
    }
    
    div[data-testid="column"]:last-child button[data-testid="baseButton-secondary"]:hover {
        background-color: #3367d6 !important;
        border-color: #3367d6 !important;
    }
    
    /* 피드백 닫기 버튼을 더 작게 */
    button[key="close_feedback_msg"] {
        min-height: 1.5rem !important;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        width: 2rem !important;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #4285f4 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
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
    
    # 현재 페이지 확인
    current_page = st.session_state.get('current_page', 'main')
    
    # 사이드바 표시 (모든 페이지에서)
    show_sidebar(
        st.session_state.user_id, 
        st.session_state.team_name, 
        st.session_state.user_name
    )
    
    # 콘텐츠 이력 표시 (제거됨)
    # show_content_history(st.session_state.user_id)
    
    if current_page == 'history':
        # 활동 히스토리 페이지
        show_history_page(st.session_state.user_id)
    elif current_page == 'community_cases':
        # 커뮤니티별 사례 페이지
        show_community_cases_page(st.session_state.user_id)
    else:
        # 메인 페이지 (기본)
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
