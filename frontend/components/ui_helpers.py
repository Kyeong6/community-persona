import streamlit as st
import pyperclip
import platform

from services import copy_action, get_user_content_history
from database.crud import record_content_adoption, update_content_text, get_content_adopted_tones
from utils.get_logger import get_logger

# 로거 초기화
logger = get_logger()

# 성공 메시지 표시
def show_success_message(message: str):
    st.success(message)

# 에러 메시지 표시
def show_error_message(message: str):
    st.error(message)

# 정보 메시지 표시
def show_info_message(message: str):
    st.info(message)

# 클립보드에 텍스트 복사
def copy_to_clipboard(text: str) -> bool:
    """
    텍스트를 클립보드에 복사합니다.
    주의: Streamlit은 웹 앱이므로 브라우저 보안 정책상 서버 측 클립보드 접근이 제한됩니다.
    사용자는 텍스트 영역을 직접 선택하여 복사해야 합니다.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 로컬 환경에서만 작동할 수 있습니다
        pyperclip.copy(text)
        return True
    except Exception:
        # 웹 환경에서는 항상 False를 반환
        # 사용자는 텍스트를 직접 선택하여 복사 가능
        return False

# 운영체제별 복사 메시지 반환
def get_platform_copy_message() -> str:
    if platform.system() == "Darwin":  # macOS
        return "✅ 원고가 클립보드에 복사되었습니다! \nCmd+V로 붙여넣기하세요."
    elif platform.system() == "Windows":  # Windows
        return "✅ 원고가 클립보드에 복사되었습니다! \nCtrl+V로 붙여넣기하세요."
    else:  # 기타 (지원하지 않는 OS)
        return "✅ 원고가 클립보드에 복사되었습니다!"

# 복사 성공 메시지 표시 (닫기 버튼 포함)
def show_copy_success_message(key: str):
    """복사 성공 메시지를 표시하고 닫기 버튼을 제공합니다."""
    message = get_platform_copy_message()
    # \n을 <br>로 변환하여 HTML에서 줄바꿈이 제대로 표시되도록 함
    message_html = message.replace('\n', '<br>')
    
    # 메시지와 닫기 버튼을 같은 행에 배치
    col_msg, col_btn = st.columns([4, 1])
    
    with col_msg:
        # 배경색이 있는 컨테이너로 표시
        st.markdown(f"""
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 12px; color: #155724;">
            {message_html}
        </div>
        """, unsafe_allow_html=True)
    
    with col_btn:
        # 닫기 버튼을 세로 중앙에 배치
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 맞추기
        if st.button("✖️ 닫기", key=f"close_copy_{key}", use_container_width=True):
            st.session_state[f'copy_message_{key}'] = False
            st.rerun()

# 복사 실패 메시지 표시
def show_copy_failure_message():
    st.error("❌ 클립보드 복사에 실패했습니다. 텍스트를 수동으로 복사해주세요.")
    
    if platform.system() == "Darwin":  # macOS
        st.info("💡 텍스트를 마우스로 드래그하여 선택한 후 Cmd+C로 복사하세요.")
    elif platform.system() == "Windows":  # Windows
        st.info("💡 텍스트를 마우스로 드래그하여 선택한 후 Ctrl+C로 복사하세요.")
    else:
        st.info("💡 텍스트를 마우스로 드래그하여 선택한 후 복사하세요.")

# 상품 정보 포맷팅
def format_product_info(product_info: dict) -> str:
    return f"상품: {product_info.get('product_name', '')} | 가격: {product_info.get('price', '')}"

# 속성 정보 포맷팅
def format_attributes(attributes: dict) -> str:
    community = attributes.get('community', '')
    category = attributes.get('category', '')
    return f"커뮤니티: {community} | 카테고리: {category}"

# 콘텐츠 카드 생성
def create_content_cards(contents: list, session_state: dict):
    cols = st.columns(3)
    
    # 복사한 톤 정보 조회
    current_generate_id = session_state.get('current_generate_id')
    adopted_tones = []
    if current_generate_id:
        adopted_tones = get_content_adopted_tones(current_generate_id)
    
    for i, content in enumerate(contents):
        with cols[i % 3]:
            # 카드 컨테이너
            with st.container():
                # 복사한 톤인지 확인
                is_adopted = content['tone'] in adopted_tones
                
                # 헤더와 설명
                tone_descriptions = {
                    '정보전달형': '상품의 <strong style="color: #1f40af;">최종 가격 조건과 핵심 스펙</strong>만 빠르고 객관적으로 요약하여 전달',
                    '후기형': '직접 써본 경험과 <strong style="color: #1f40af;">솔직한 만족도</strong>를 공유해 구매를 망설이는 잠재 고객을 설득',
                    '유머러스한 형': '<strong style="color: #1f40af;">밈, 위트</strong>를 활용해 게시물의 재미를 높여 젊은 층의 관심과 공유를 유도',
                    '친근한 톤': '경험과 고민을 언급하며 사용자들과 친밀하게 소통하고 <strong style="color: #1f40af;">부드럽게 상품을 추천</strong>',
                    '긴급/마감 임박형': '<strong style="color: #1f40af;">한정 수량, 마감 임박, 역대 최저가</strong>를 강조하여 고객의 구매 행동을 이끌어냄',
                    '스토리텔링형': '<strong style="color: #1f40af;">구체적인 일상 에피소드</strong>를 통해 상품의 필요성과 구매 당위성을 강조'
                }
                
                description = tone_descriptions.get(content['tone'], '')
                
                # 복사한 톤이면 강조 표시
                adopted_icon = ' ✅' if is_adopted else ''
                border_color = '#28a745' if is_adopted else '#3b82f6'
                shadow_style = 'box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);' if is_adopted else 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);'
                
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 6px; color: #1f2937;">
                        {content['tone']}{adopted_icon}
                    </div>
                    <div style="font-size: 12px; color: #4b5563; line-height: 1.5; background: #f8fafc; padding: 8px 10px; border-radius: 6px; border-left: 4px solid {border_color}; {shadow_style}">
                        {description}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 원고 내용 - 채택 여부에 따라 배경색 변경
                current_generate_id = session_state.get('current_generate_id', 'default')
                content_bg_color = '#e8f5e8' if is_adopted else '#f8f9fa'
                content_border_color = '#28a745' if is_adopted else '#dee2e6'
                
                # 수정 모드가 아니면 표시
                if not session_state.get(f"editing_{content['id']}", False):
                    # 수정 모드가 아니고 세션에 업데이트된 텍스트가 있으면 그것을 사용
                    display_text = content['text']
                    for c in session_state.get('generated_contents', []):
                        if c['id'] == content['id']:
                            display_text = c.get('text', content['text'])
                            break
                    
                    # 채택된 톤은 다른 배경색으로 표시 (선택 가능하게)
                    if is_adopted:
                        st.markdown(f"""
                        <div style="background-color: {content_bg_color}; border: 2px solid {content_border_color}; border-radius: 8px; padding: 12px; margin: 8px 0; cursor: text;">
                            <pre style="margin: 0; font-family: inherit; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.6; color: #212529; user-select: all;">{display_text}</pre>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.text_area(
                            "", 
                            value=display_text, 
                            height=150, 
                            key=f"content_{current_generate_id}_{content['id']}",
                            disabled=False,
                            label_visibility="collapsed"
                        )
                
                # 수정 모드 확인
                if session_state.get(f"editing_{content['id']}", False):
                    # 세션에서 현재 텍스트 가져오기 (업데이트된 텍스트 포함)
                    current_text = content['text']
                    for c in session_state.get('generated_contents', []):
                        if c['id'] == content['id']:
                            current_text = c.get('text', content['text'])
                            break
                    
                    edited_text = st.text_area(
                        "원고 수정",
                        value=current_text,
                        height=200,
                        key=f"edit_content_{session_state.get('current_generate_id', 'default')}_{content['id']}"
                    )
                    
                    # 저장/취소 버튼을 오른쪽 하단에 붙여서 배치
                    st.markdown("""
                    <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px;">
                    """, unsafe_allow_html=True)
                    
                    col_save, col_cancel = st.columns([1, 1])
                    with col_save:
                        if st.button("💾 저장", key=f"save_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                            # current_generate_id 확인
                            current_generate_id = session_state.get('current_generate_id')
                            if not current_generate_id:
                                st.error("❌ 생성 ID가 없습니다. 페이지를 새로고침해주세요.")
                                return
                            
                            # 데이터베이스 업데이트
                            success = update_content_text(
                                current_generate_id,
                                int(content['id']),
                                edited_text
                            )
                            
                            if success:
                                # 세션 상태도 업데이트
                                for j, c in enumerate(session_state['generated_contents']):
                                    if c['id'] == content['id']:
                                        session_state['generated_contents'][j]['text'] = edited_text
                                        break
                                session_state[f"editing_{content['id']}"] = False
                                
                                # 수정 완료 로그
                                logger.info(f"EDIT_COMPLETE - user_id: {session_state['user_id']}, content_id: {current_generate_id}, tone: {content.get('tone', 'Unknown')}")
                                
                                st.success("원고가 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"수정 중 오류가 발생했습니다. generate_id: {session_state.get('current_generate_id', 'None')}, content_id: {content['id']}")
                    
                    with col_cancel:
                        if st.button("❌ 취소", key=f"cancel_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                            session_state[f"editing_{content['id']}"] = False
                            st.rerun()
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 원고 내용은 이미 위에서 표시됨 (복사한 톤에 따라 다른 색상)
                    pass
                
                # 액션 버튼 - 붙여서 배치
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"📋 복사", key=f"copy_{session_state.get('current_generate_id', 'default')}_{content['id']}", use_container_width=True):
                        # tone 변수 정의
                        tone = content.get('tone', 'Unknown')
                        current_generate_id = session_state.get('current_generate_id', 'temp_id')
                        
                        # 기존 copy_action 호출
                        copy_action(
                            session_state['user_id'],
                            current_generate_id,
                            str(content['id']),
                            tone=tone
                        )
                        # 채택 기록 저장
                        record_content_adoption(
                            session_state['user_id'],
                            current_generate_id,
                            tone
                        )
                        
                        # 복사 행동 로그 기록
                        logger.info(f"COPY_ACTION - user_id: {session_state['user_id']}, content_id: {current_generate_id}, tone: {tone}, community: {session_state.get('selected_community')}")
                        
                        # 안내 메시지
                        st.success("✅ 복사 완료! 위의 텍스트를 선택한 후 **Ctrl+C**로 복사하세요.")
                        st.rerun()
                
                with col2:
                    if st.button(f"✏️ 수정", key=f"edit_{session_state.get('current_generate_id', 'default')}_{content['id']}", use_container_width=True):
                        # 수정 시작 로그
                        logger.info(f"EDIT_START - user_id: {session_state['user_id']}, content_id: {session_state.get('current_generate_id', 'temp_id')}, tone: {content.get('tone', 'Unknown')}")
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
