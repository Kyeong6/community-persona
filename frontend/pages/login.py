import streamlit as st

from services import handle_user_login
from ..components.ui_helpers import show_success_message, show_error_message


def show_user_login_screen():
    """사용자 확인 화면"""
    st.markdown("""
    <div class="main-header">
        <h1>👤 사용자 확인</h1>
        <p>팀명과 사용자명을 입력하여 서비스를 이용하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.subheader("📝 사용자 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 팀명 리스트 (가나다 순서)
            team_options = [
                "브랜드패션팀",
                "뷰티팀", 
                "명품잡화/직구팀",
                "스포츠레저팀",
                "유아동패션팀",
                "트렌드패션팀"
            ]
            
            team_name = st.selectbox(
                "팀명 *",
                options=team_options,
                index=None,
                placeholder="팀을 선택하세요",
                help="소속 팀을 선택하세요"
            )
        
        with col2:
            user_name = st.text_input(
                "사용자명 *",
                placeholder="홍길동, 이순신",
                help="사용자명을 입력하세요"
            )
        
        st.divider()
        
        # 로그인 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🔐 로그인",
                type="primary",
                use_container_width=True,
                help="팀명을 선택하고 사용자명을 입력한 후 로그인하세요"
            ):
                if team_name and user_name:
                    user_id = handle_user_login(team_name, user_name)
                    st.session_state.user_id = user_id
                    st.session_state.team_name = team_name
                    st.session_state.user_name = user_name
                    st.session_state.user_logged_in = True
                    show_success_message(f"로그인 성공! 사용자 ID: {user_id}")
                    st.rerun()
                else:
                    show_error_message("팀명을 선택하고 사용자명을 입력해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 하단 안내
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 14px;'>* 팀명을 선택하고 사용자명을 입력한 후 로그인하세요</p>",
            unsafe_allow_html=True
        )
