import streamlit as st
from datetime import datetime
from services.user_service import get_user_history
from services import user_feedback
from utils.get_logger import get_logger

# 로거 초기화
logger = get_logger()

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
        
        # 현재 페이지 확인
        current_page = st.session_state.get('current_page', 'main')
        
        # 상품 정보 기입 페이지 (메인)
        if current_page == 'main':
            st.button("📝 상품 정보 기입", use_container_width=True, disabled=True, help="현재 페이지")
        else:
            if st.button("📝 상품 정보 기입", use_container_width=True):
                st.session_state.current_page = "main"
                st.session_state.show_results = False
                st.rerun()
        
        # 활동 히스토리 페이지
        if current_page == 'history':
            st.button("📊 활동 히스토리", use_container_width=True, disabled=True, help="현재 페이지")
        else:
            if st.button("📊 활동 히스토리", use_container_width=True):
                st.session_state.current_page = "history"
                st.rerun()
        
        # 커뮤니티별 베스트 사례 페이지
        if current_page == 'community_cases':
            st.button("🏘️ 커뮤니티별 베스트 사례", use_container_width=True, disabled=True, help="현재 페이지")
        else:
            if st.button("🏘️ 커뮤니티별 베스트 사례", use_container_width=True):
                st.session_state.current_page = "community_cases"
                st.rerun()
        
        st.divider()
        
        # 피드백 섹션 (맨 아래로 이동)
        st.markdown("### 💬 피드백")
        
        # 피드백 전송 성공 메시지 표시
        if hasattr(st.session_state, 'feedback_sent') and st.session_state.feedback_sent:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.success("🎉 피드백이 전송되었습니다!")
            with col2:
                if st.button("✕", key="close_feedback_msg", help="메시지 닫기", use_container_width=True):
                    st.session_state.feedback_sent = False
                    st.rerun()
        
        # 별점 평가
        st.markdown("**⭐ 서비스 만족도**")
        
        rating = st.select_slider(
            "별점을 선택해주세요",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x,
            help="1점(매우 불만족) ~ 5점(매우 만족)",
            key="main_sidebar_rating"
        )
        
        # 별점 표시
        st.markdown(f"**선택된 별점:** {'⭐' * rating} ({rating}점)")
        
        feedback_text = st.text_area(
            "서비스 개선을 위한 피드백을 남겨주세요!",
            placeholder="개선사항이나 의견을 자유롭게 작성해주세요",
            height=100,
            help="여러분의 소중한 의견이 더 나은 서비스로 이어집니다😄",
            key="main_sidebar_feedback"
        )
        
        if st.button("📝 피드백 전송", use_container_width=True):
            if feedback_text.strip() or rating != 5:  # 별점이 5점이 아니거나 텍스트가 있으면 전송
                try:
                    # 피드백 제출 로그 기록
                    logger.info(f"FEEDBACK_SUBMIT - user_id: {user_id}, rating: {rating}, has_feedback_text: {bool(feedback_text.strip())}")
                    
                    # 별점과 텍스트를 분리해서 전송
                    feedback_result = user_feedback(
                        user_id=user_id,
                        feedback_text=feedback_text.strip(),
                        rating=rating
                    )
                    
                    if feedback_result:
                        st.session_state.feedback_sent = True
                        st.rerun()
                    else:
                        st.error("피드백 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("별점을 선택하거나 피드백 내용을 입력해주세요")
