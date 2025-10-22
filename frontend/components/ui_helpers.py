import streamlit as st
import pyperclip
import platform

from services import copy_action, get_user_content_history


def show_success_message(message: str):
    """성공 메시지 표시"""
    st.success(message)


def show_error_message(message: str):
    """에러 메시지 표시"""
    st.error(message)


def show_info_message(message: str):
    """정보 메시지 표시"""
    st.info(message)


def copy_to_clipboard(text: str) -> bool:
    """클립보드에 텍스트 복사"""
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def get_platform_copy_message() -> str:
    """운영체제별 복사 메시지 반환"""
    if platform.system() == "Darwin":  # macOS
        return "✅ 원고가 클립보드에 복사되었습니다! **Cmd+V**로 붙여넣기하세요."
    elif platform.system() == "Windows":  # Windows
        return "✅ 원고가 클립보드에 복사되었습니다! **Ctrl+V**로 붙여넣기하세요."
    else:  # Linux, 기타
        return "✅ 원고가 클립보드에 복사되었습니다! **Ctrl+V**로 붙여넣기하세요."


def show_copy_success_message():
    """복사 성공 메시지 표시"""
    st.success(get_platform_copy_message())


def format_product_info(product_info: dict) -> str:
    """상품 정보 포맷팅"""
    return f"상품: {product_info.get('product_name', '')} | 가격: {product_info.get('price', '')}"


def format_attributes(attributes: dict) -> str:
    """속성 정보 포맷팅"""
    community = attributes.get('community', '')
    category = attributes.get('category', '')
    return f"커뮤니티: {community} | 카테고리: {category}"


def create_content_cards(contents: list, session_state: dict):
    """콘텐츠 카드 생성"""
    cols = st.columns(2)
    
    for i, content in enumerate(contents):
        with cols[i % 2]:
            # 카드 컨테이너
            with st.container():
                # 헤더
                st.markdown(f"**버전 {content['id']}** {content['tone']}")
                
                # 원고 내용
                st.markdown("---")
                
                # 수정 모드 확인
                if session_state.get(f"editing_{content['id']}", False):
                    edited_text = st.text_area(
                        "원고 수정",
                        value=content['text'],
                        height=200,
                        key=f"edit_content_{session_state.get('current_generate_id', 'default')}_{content['id']}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 저장", key=f"save_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                            # 수정된 내용으로 업데이트
                            for j, c in enumerate(session_state['generated_contents']):
                                if c['id'] == content['id']:
                                    session_state['generated_contents'][j]['text'] = edited_text
                                    break
                            session_state[f"editing_{content['id']}"] = False
                            st.success("원고가 수정되었습니다!")
                            st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ 취소", key=f"cancel_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                            session_state[f"editing_{content['id']}"] = False
                            st.rerun()
                else:
                    st.text_area(
                        "생성된 원고",
                        value=content['text'],
                        height=200,
                        disabled=True,
                        key=f"content_{session_state.get('current_generate_id', 'default')}_{content['id']}"
                    )
                
                # 액션 버튼
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"📋 복사", key=f"copy_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                        if copy_to_clipboard(content['text']):
                            show_copy_success_message()
                            # 복사 액션 로그 기록 (톤 정보 포함)
                            copy_action(
                                session_state['user_id'],
                                session_state['current_generate_id'],
                                str(content['id']),
                                tone=content.get('tone', 'Unknown')
                            )
                
                with col_btn2:
                    if st.button(f"✏️ 수정", key=f"edit_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                        session_state[f"editing_{content['id']}"] = True
                        st.rerun()
                
                st.markdown("")  # 간격


def show_user_info(team_name: str, user_name: str, user_id: str):
    """사용자 정보 표시"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <strong>👤 로그인된 사용자:</strong> {team_name} - {user_name} 
            <span style="color: #666;">(ID: {user_id})</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 로그아웃", type="secondary", use_container_width=True):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def show_content_history(user_id: str):
    """콘텐츠 이력 표시"""
    with st.sidebar:
        st.markdown("### 📚 콘텐츠 이력")
        try:
            user_generations = get_user_content_history(user_id, limit=5)
            if user_generations:
                for i, generation in enumerate(user_generations):
                    with st.expander(f"{generation.product_info.get('product_name', '상품명')} - {generation.created_at[:16]}", expanded=False):
                        st.write(f"**상품:** {generation.product_info.get('product_name', '')}")
                        st.write(f"**가격:** {generation.product_info.get('price', '')}")
                        st.write(f"**커뮤니티:** {generation.attributes.get('community', '')}")
                        if st.button(f"📋 불러오기", key=f"load_{i}"):
                            st.session_state.generated_contents = generation.generated_contents
                            st.session_state.show_results = True
                            st.rerun()
            else:
                st.write("생성된 콘텐츠가 없습니다.")
        except Exception as e:
            st.write("콘텐츠 이력을 불러올 수 없습니다.")
