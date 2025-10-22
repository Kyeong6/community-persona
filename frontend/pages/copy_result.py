import os
import sys
import streamlit as st

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services import regenerate_copy, user_feedback
from ..components.ui_helpers import create_content_cards


def show_results_screen():
    """결과 화면 표시"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2>📝 생성된 원고</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 결과 그리드
    create_content_cards(st.session_state.generated_contents, st.session_state)
    
    # 하단 액션 버튼 (기존 3개 버튼으로 복원)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← 입력 화면으로", use_container_width=True):
            st.session_state.show_results = False
            st.rerun()
    
    with col2:
        if st.button("🔄 새로운 원고 생성", use_container_width=True):
            st.session_state.show_results = False
            st.rerun()
    
    with col3:
        if st.button("✨ 다시 생성하기", type="primary", use_container_width=True):
            # 재생성 이유 입력 모달 표시
            st.session_state.show_regenerate_modal = True
            st.rerun()
    
    # 재생성 모달
    if st.session_state.get('show_regenerate_modal', False):
        st.markdown("---")
        st.markdown("### 🔄 재생성 이유 입력")
        
        regenerate_reason = st.text_area(
            "어떤 부분을 개선하고 싶으신가요?",
            placeholder="예: 톤이 너무 딱딱해요, 더 자연스러운 표현이 필요해요, 특정 키워드가 더 강조되었으면 좋겠어요",
            height=100,
            help="재생성 이유를 구체적으로 입력해주세요"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("취소", use_container_width=True):
                st.session_state.show_regenerate_modal = False
                st.rerun()
        
        with col2:
            if st.button("재생성", type="primary", use_container_width=True):
                if regenerate_reason.strip():
                    try:
                        # 백엔드 재생성 서비스 호출
                        result = regenerate_copy(
                            user_id=st.session_state.user_id,
                            generate_id=st.session_state.current_generate_id,
                            reason_text=regenerate_reason
                        )
                        
                        if result and result.get("generate_id"):
                            st.session_state.generated_contents = result["generated_contents"]
                            st.session_state.current_generate_id = result.get("generate_id", "temp_id")
                            st.session_state.show_regenerate_modal = False
                            st.success("재생성 완료! 새로운 문구를 확인해보세요.")
                            st.rerun()
                        else:
                            st.error(f"재생성에 실패했습니다: {result.get('error', '알 수 없는 오류')}")
                    except Exception as e:
                        st.error(f"재생성 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.warning("재생성 이유를 입력해주세요")
    
    # 피드백 섹션 (맨 아래로 이동)
    st.markdown("---")
    st.markdown("### 💬 결과에 대한 피드백")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        feedback_text = st.text_area(
            "생성된 문구에 대한 피드백을 남겨주세요",
            placeholder="예: 톤이 너무 딱딱해요, 더 자연스러운 표현이 필요해요, 특정 키워드가 더 강조되었으면 좋겠어요",
            height=100,
            help="여러분의 피드백이 더 나은 문구 생성에 도움이 됩니다"
        )
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("📝 피드백 전송", use_container_width=True):
            if feedback_text.strip():
                try:
                    # 실제 백엔드 피드백 서비스 호출
                    feedback_result = user_feedback(
                        user_id=st.session_state.user_id,
                        feedback_text=feedback_text
                    )
                    
                    if feedback_result:
                        st.success("피드백이 전송되었습니다! 감사합니다 🙏")
                        st.rerun()
                    else:
                        st.error("피드백 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("피드백 내용을 입력해주세요")
