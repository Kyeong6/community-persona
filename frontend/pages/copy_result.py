import streamlit as st

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
            # 새로운 원고 생성 시 모든 입력값 초기화
            st.session_state.show_results = False
            # 입력값 초기화 플래그 설정
            st.session_state.clear_inputs = True
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
            placeholder="요구사항을 구체적으로 입력해주시면 더 나은 문구를 생성해드릴게요!",
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
                        # 로딩 위젯 표시
                        with st.spinner("🔄 문구를 재생성하고 있습니다..."):
                            # 백엔드 재생성 서비스 호출
                            result = regenerate_copy(
                                user_id=st.session_state.user_id,
                                generate_id=st.session_state.current_generate_id,
                                reason_text=regenerate_reason
                            )
                        
                        if result and result.get("generate_id"):
                            # 세션 상태 강제 업데이트
                            st.session_state.generated_contents = result["generated_contents"]
                            st.session_state.current_generate_id = result.get("generate_id", "temp_id")
                            st.session_state.show_regenerate_modal = False
                            
                            # 성공 메시지 표시
                            st.success("재생성 완료! 새로운 문구를 확인해보세요.")
                            
                            # 페이지 강제 새로고침
                            st.rerun()
                        else:
                            st.error(f"재생성에 실패했습니다: {result.get('error', '알 수 없는 오류')}")
                    except Exception as e:
                        st.error(f"재생성 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.warning("재생성 이유를 입력해주세요")
    
