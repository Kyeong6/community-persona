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
    
    # 하단 액션 버튼
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
