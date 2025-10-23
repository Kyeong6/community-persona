import streamlit as st
from datetime import datetime
from services.user_service import get_user_history
from services import user_feedback

def show_sidebar(user_id: str, team_name: str, user_name: str):
    """
    왼쪽 사이드바를 표시합니다.
    피드백 기능과 사용자 히스토리를 포함합니다.
    """
    with st.sidebar:
        # 사용자 정보
        st.markdown("### 👤 사용자 정보")
        st.markdown(f"**팀:** {team_name}")
        st.markdown(f"**이름:** {user_name}")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", type="secondary", use_container_width=True):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # 네비게이션 섹션
        st.markdown("### 🧭 페이지 이동")
        
        # 활동 히스토리 버튼
        if st.button("📊 활동 히스토리", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()
        
        # 커뮤니티별 사례 버튼
        if st.button("🏘️ 커뮤니티별 사례", use_container_width=True):
            st.session_state.current_page = "community_cases"
            st.rerun()
        
        st.divider()
        
        # 피드백 섹션 (맨 아래로 이동)
        st.markdown("### 💬 피드백")
        
        # 피드백 전송 성공 메시지 표시
        if hasattr(st.session_state, 'feedback_sent') and st.session_state.feedback_sent:
            st.success("🎉 피드백이 전송되었습니다!")
            st.session_state.feedback_sent = False
        
        feedback_text = st.text_area(
            "서비스 개선을 위한 피드백을 남겨주세요!",
            placeholder="예: 더 다양한 톤의 문구가 필요해요, 특정 키워드 강조 기능이 있었으면 좋겠어요",
            height=100,
            help="여러분의 소중한 의견이 더 나은 서비스로 이어집니다😄",
            key="sidebar_feedback"
        )
        
        if st.button("📝 피드백 전송", use_container_width=True):
            if feedback_text.strip():
                try:
                    feedback_result = user_feedback(
                        user_id=user_id,
                        feedback_text=feedback_text
                    )
                    
                    if feedback_result:
                        st.session_state.feedback_sent = True
                        st.rerun()
                    else:
                        st.error("피드백 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("피드백 내용을 입력해주세요")
