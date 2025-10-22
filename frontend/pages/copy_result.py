"""
결과 표시 페이지
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
            # 현재 입력값들을 유지하면서 다시 생성
            st.rerun()
    
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
                # 임시 피드백 처리 (백엔드 연결 전)
                st.success("피드백이 전송되었습니다! 감사합니다 🙏")
                st.rerun()
            else:
                st.warning("피드백 내용을 입력해주세요")
