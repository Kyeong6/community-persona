import streamlit as st
import pyperclip
import platform

from services import copy_action
from database.crud import record_content_adoption
from database.crud import update_content_text

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
    try:
        # 먼저 pyperclip 시도
        pyperclip.copy(text)
        return True
    except Exception:
        # pyperclip 실패 시 운영체제별 네이티브 명령어 사용
        try:
            import subprocess
            
            if platform.system() == "Windows":
                # Windows: clip 명령어 사용
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True, shell=True)
                process.communicate(input=text)
                return process.returncode == 0
            elif platform.system() == "Darwin":
                # macOS: pbcopy 사용
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                return process.returncode == 0
            else:
                return False
        except Exception:
            return False

# 운영체제별 복사 메시지 반환
def get_platform_copy_message() -> str:
    if platform.system() == "Darwin":  # macOS
        return "✅ 원고가 클립보드에 복사되었습니다! \n**Cmd+V**로 붙여넣기하세요."
    elif platform.system() == "Windows":  # Windows
        return "✅ 원고가 클립보드에 복사되었습니다! \n**Ctrl+V**로 붙여넣기하세요."
    else:  # 기타 (지원하지 않는 OS)
        return "✅ 원고가 클립보드에 복사되었습니다!"

# 복사 성공 메시지 표시
def show_copy_success_message():
    st.success(get_platform_copy_message())

# 복사 실패 메시지 표시
def show_copy_failure_message():
    st.error("❌ 클립보드 복사에 실패했습니다. 텍스트를 수동으로 복사해주세요.")
    
    if platform.system() == "Darwin":  # macOS
        st.info("💡 텍스트를 마우스로 드래그하여 선택한 후 **Cmd+C**로 복사하세요.")
    elif platform.system() == "Windows":  # Windows
        st.info("💡 텍스트를 마우스로 드래그하여 선택한 후 **Ctrl+C**로 복사하세요.")
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
    
    for i, content in enumerate(contents):
        with cols[i % 3]:
            # 카드 컨테이너
            with st.container():
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
                
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 6px; color: #1f2937;">
                        {content['tone']}
                    </div>
                    <div style="font-size: 12px; color: #4b5563; line-height: 1.5; background: #f8fafc; padding: 8px 10px; border-radius: 6px; border-left: 4px solid #3b82f6; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                        {description}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 원고 내용
                
                # 수정 모드 확인
                if session_state.get(f"editing_{content['id']}", False):
                    edited_text = st.text_area(
                        "원고 수정",
                        value=content['text'],
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
                            # 데이터베이스 업데이트
                            success = update_content_text(
                                session_state.get('current_generate_id', ''),
                                content['id'],
                                edited_text
                            )
                            
                            if success:
                                # 세션 상태도 업데이트
                                for j, c in enumerate(session_state['generated_contents']):
                                    if c['id'] == content['id']:
                                        session_state['generated_contents'][j]['text'] = edited_text
                                        break
                                session_state[f"editing_{content['id']}"] = False
                                st.success("원고가 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error("수정 중 오류가 발생했습니다.")
                    
                    with col_cancel:
                        if st.button("❌ 취소", key=f"cancel_{session_state.get('current_generate_id', 'default')}_{content['id']}"):
                            session_state[f"editing_{content['id']}"] = False
                            st.rerun()
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 가독성을 위해 마크다운으로 표시 (고정 높이 + 스크롤)
                    st.markdown(f"""
                    <div style="
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #212529;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        height: 150px;
                        overflow-y: auto;
                        overflow-x: hidden;
                    ">{content['text']}</div>
                    """, unsafe_allow_html=True)
                
                # 액션 버튼 - 붙여서 배치
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"📋 복사", key=f"copy_{session_state.get('current_generate_id', 'default')}_{content['id']}", use_container_width=True):
                        if copy_to_clipboard(content['text']):
                            show_copy_success_message()
                            # 기존 copy_action 호출
                            copy_action(
                                session_state['user_id'],
                                session_state['current_generate_id'],
                                str(content['id']),
                                tone=content.get('tone', 'Unknown')
                            )
                            # 채택 기록 저장
                            record_content_adoption(
                                session_state['user_id'],
                                str(content['id']),
                                content.get('tone', 'Unknown')
                            )
                        else:
                            show_copy_failure_message()
                
                with col2:
                    if st.button(f"✏️ 수정", key=f"edit_{session_state.get('current_generate_id', 'default')}_{content['id']}", use_container_width=True):
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
