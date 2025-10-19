import streamlit as st
import pandas as pd
from datetime import datetime, date
import random

# 페이지 설정
st.set_page_config(
    page_title="커뮤니티 바이럴 콘텐츠 생성 시스템",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .emphasis-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
    }
    
    .emphasis-badge.selected {
        background: #1976d2;
        color: white;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'team_name' not in st.session_state:
    st.session_state.team_name = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'generated_contents' not in st.session_state:
    st.session_state.generated_contents = []
if 'selected_emphasis' not in st.session_state:
    st.session_state.selected_emphasis = []
if 'emphasis_details' not in st.session_state:
    st.session_state.emphasis_details = []
if 'content_history' not in st.session_state:
    st.session_state.content_history = []

def handle_user_login(team_name: str, user_name: str):
    """사용자 식별 및 등록 함수"""
    import hashlib
    import time
    
    # 고유 user_id 생성 (팀명 + 사용자명 + 타임스탬프 기반)
    timestamp = str(int(time.time()))
    user_string = f"{team_name}_{user_name}_{timestamp}"
    user_id = hashlib.md5(user_string.encode()).hexdigest()[:12]
    
    # 세션 상태 업데이트
    st.session_state.user_id = user_id
    st.session_state.team_name = team_name
    st.session_state.user_name = user_name
    st.session_state.user_logged_in = True
    
    return user_id

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
            team_name = st.text_input(
                "팀명 *",
                placeholder="예: 뷰티팀, 브랜드패션팀",
                help="소속 팀명을 입력하세요"
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
                help="팀명과 사용자명을 입력한 후 로그인하세요"
            ):
                if team_name and user_name:
                    user_id = handle_user_login(team_name, user_name)
                    st.success(f"로그인 성공! 사용자 ID: {user_id}")
                    st.rerun()
                else:
                    st.error("팀명과 사용자명을 모두 입력해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 하단 안내
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 14px;'>* 팀명과 사용자명을 입력한 후 로그인하세요</p>",
            unsafe_allow_html=True
        )

def generate_content(product_name, price, start_date, end_date, community, emphasis_details, best_case=""):
    """원고 생성 함수"""
    
    # 커뮤니티별 톤 조정
    community_tones = {
        'ppomppu': ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'],
        'fmkorea': ['정보 전달형', '후기형', '친근한 톤', '유머러스한 톤'],
        'womad': ['후기형', '친근한 톤', '정보 전달형', '유머러스한 톤']
    }
    
    tones = community_tones.get(community, ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'])
    
    # 강조사항 텍스트 생성
    emphasis_text = '\n'.join([f"• {detail}" for detail in emphasis_details]) if emphasis_details else ""
    
    # 날짜 포맷팅
    start_str = start_date.strftime('%m월 %d일') if start_date else ""
    end_str = end_date.strftime('%m월 %d일') if end_date else ""
    
    # 커뮤니티명 변환
    community_names = {
        'ppomppu': '뽐뿌',
        'fmkorea': '에펨코리아', 
        'womad': '여성시대'
    }
    community_name = community_names.get(community, community)
    
    # 각 톤별 원고 생성
    contents = []
    
    # 1. 친근한 톤
    contents.append({
        'id': 1,
        'tone': '친근한 톤',
        'text': f"""{product_name} 이거 진짜 대박이에요 ㄷㄷ

작년에 {price}에 샀는데 지금 보니까 또 세일하네요.
이 가격에 이 퀄리티면 가성비 ㅇㅈ?

{emphasis_text}

놓치면 후회할 듯... 저는 재구매 각입니다 👍"""
    })
    
    # 2. 정보 전달형
    contents.append({
        'id': 2,
        'tone': '정보 전달형',
        'text': f"""{product_name} 특가 정보 공유합니다.

가격: {price}
기간: {start_str} ~ {end_str}

{emphasis_text}

비교해보니 역대급 가격인 것 같아서 올립니다.
필요하신 분들 참고하세요!"""
    })
    
    # 3. 후기형
    contents.append({
        'id': 3,
        'tone': '후기형',
        'text': f"""{product_name} 쓴지 3개월 됐는데 후기 남깁니다.

솔직히 처음엔 {price} 주고 사기 좀 망설였는데
지금은 완전 만족 중이에요 ㅎㅎ

{emphasis_text}

지금 또 세일한다길래 주변에 추천하려고 글 올려요.
고민하시는 분들한테는 강추!"""
    })
    
    # 4. 유머러스한 톤
    contents.append({
        'id': 4,
        'tone': '유머러스한 톤',
        'text': f"""{product_name} {price}이라니...

(이거 사야되나 말아야되나 고민중)

{emphasis_text}

지갑: 안돼...😭
나: 어차피 살 거 지금 사는 게 이득 아니야?
지갑: ...💸

결국 또 질렀습니다 여러분 ㅋㅋㅋ
같이 망하실 분? 🙋‍♀️"""
    })
    
    return contents

def main():
    # 사용자 로그인 확인
    if not st.session_state.user_logged_in:
        show_user_login_screen()
        return
    
    # 로그인된 사용자 정보 표시
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <strong>👤 로그인된 사용자:</strong> {st.session_state.team_name} - {st.session_state.user_name} 
            <span style="color: #666;">(ID: {st.session_state.user_id})</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 로그아웃", type="secondary", use_container_width=True):
            # 세션 상태 초기화
            st.session_state.user_logged_in = False
            st.session_state.user_id = None
            st.session_state.team_name = None
            st.session_state.user_name = None
            st.session_state.show_results = False
            st.session_state.generated_contents = []
            st.rerun()
    
    # 사이드바 - 콘텐츠 이력
    with st.sidebar:
        st.markdown("### 📚 콘텐츠 이력")
        if st.session_state.content_history:
            for i, entry in enumerate(reversed(st.session_state.content_history[-5:])):  # 최근 5개만 표시
                with st.expander(f"{entry['product_name']} - {entry['timestamp'][:16]}", expanded=False):
                    st.write(f"**팀:** {entry['team_name']}")
                    st.write(f"**사용자:** {entry['user_name']}")
                    st.write(f"**상품:** {entry['product_name']}")
                    st.write(f"**가격:** {entry['price']}")
                    st.write(f"**커뮤니티:** {entry['community']}")
                    if st.button(f"📋 불러오기", key=f"load_{i}"):
                        st.session_state.generated_contents = entry['generated_contents']
                        st.session_state.show_results = True
                        st.rerun()
        else:
            st.write("생성된 콘텐츠가 없습니다.")
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>✨ 커뮤니티 바이럴 콘텐츠 생성 시스템</h1>
        <p>상품 정보를 입력하고 커뮤니티에 맞는 원고를 자동으로 생성하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_results:
        # 입력 폼
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            
            # 기본 정보
            st.subheader("📝 기본 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input(
                    "상품명 *",
                    placeholder="예: 나이키 에어맥스 270",
                    help="생성할 상품의 이름을 입력하세요"
                )
            
            with col2:
                price = st.text_input(
                    "가격 *",
                    placeholder="예: 89,000원",
                    help="상품의 가격을 입력하세요"
                )
            
            st.divider()
            
            # 타겟 설정
            st.subheader("🎯 타겟 설정")
            col1, col2 = st.columns(2)
            
            with col1:
                category = st.selectbox(
                    "카테고리 *",
                    options=["fashion", "beauty"],
                    format_func=lambda x: "패션" if x == "fashion" else "뷰티",
                    help="상품의 카테고리를 선택하세요"
                )
            
            with col2:
                community = st.selectbox(
                    "타겟 커뮤니티 *",
                    options=["ppomppu", "fmkorea", "womad"],
                    format_func=lambda x: {
                        "ppomppu": "뽐뿌",
                        "fmkorea": "에펨코리아",
                        "womad": "여성시대"
                    }[x],
                    help="타겟으로 할 커뮤니티를 선택하세요"
                )
            
            st.divider()
            
            # 강조 사항
            st.subheader("⭐ 강조 사항")
            
            emphasis_options = ['쿠폰', '이벤트', '특정 키워드', '카드 혜택', '기타']
            emphasis_placeholders = {
                '쿠폰': '예: 신규회원 20% 할인 쿠폰, 최대 5만원까지',
                '이벤트': '예: 첫 구매 시 추가 5,000원 할인 + 무료배송',
                '특정 키워드': '예: 한정수량, 조기품절, 인기상품',
                '카드 혜택': '예: 신한카드 5% 할인, 삼성카드 3만원 적립',
                '기타': '상세 내용을 입력하세요'
            }
            
            # 강조사항 선택
            selected_emphasis = st.multiselect(
                "강조 사항 종류 선택",
                options=emphasis_options,
                default=[],
                help="원고에 포함할 강조사항을 선택하세요"
            )
            
            emphasis_details = []
            
            # 선택된 강조사항별 상세 입력
            if selected_emphasis:
                st.markdown("**상세 내용 입력:**")
                for emphasis_type in selected_emphasis:
                    with st.expander(f"📌 {emphasis_type}", expanded=True):
                        emphasis_text = st.text_area(
                            f"{emphasis_type} 상세 내용",
                            placeholder=emphasis_placeholders[emphasis_type],
                            key=f"emphasis_{emphasis_type}",
                            height=100
                        )
                        if emphasis_text.strip():
                            emphasis_details.append(emphasis_text.strip())
            
            st.divider()
            
            # 베스트 사례 (선택사항)
            with st.expander("⭐ 베스트 사례 (선택사항)", expanded=False):
                st.markdown("이전에 효과가 좋았던 원고 문구를 입력하세요")
                st.markdown("*예: '이거 진짜 대박... 작년에 샀는데 아직도 잘 신고 있음. 이 가격에 이 퀄이면 가성비 ㅇㅈ?'*")
                
                best_case = st.text_area(
                    "베스트 사례 원고",
                    placeholder="좋은 반응을 얻었던 원고 문구나 표현 방식을 자유롭게 입력하세요. 여러 개를 작성해도 좋습니다.",
                    height=150,
                    help="💡 입력하신 베스트 사례는 AI 학습에 활용되어 더 나은 원고를 생성하는 데 도움이 됩니다."
                )
            
            st.divider()
            
            # 생성 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "✨ 원고 생성하기",
                    type="primary",
                    use_container_width=True,
                    help="입력한 정보를 바탕으로 4개의 다른 톤의 원고를 생성합니다"
                ):
                    if product_name and price:
                        with st.spinner("원고를 생성하고 있습니다..."):
                            generated_contents = generate_content(
                                product_name, price, None, None, 
                                community, emphasis_details, best_case
                            )
                            st.session_state.generated_contents = generated_contents
                            st.session_state.show_results = True
                            
                            # 콘텐츠 이력에 저장
                            history_entry = {
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'user_id': st.session_state.user_id,
                                'team_name': st.session_state.team_name,
                                'user_name': st.session_state.user_name,
                                'product_name': product_name,
                                'price': price,
                                'community': community,
                                'emphasis_details': emphasis_details,
                                'best_case': best_case,
                                'generated_contents': generated_contents
                            }
                            st.session_state.content_history.append(history_entry)
                            st.rerun()
                    else:
                        st.error("상품명과 가격은 필수 입력 항목입니다.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 하단 안내
            st.markdown("---")
            st.markdown(
                "<p style='text-align: center; color: #666; font-size: 14px;'>* 필수 입력 항목을 모두 작성한 후 원고를 생성하세요</p>",
                unsafe_allow_html=True
            )
    
    else:
        # 결과 화면
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>📝 생성된 원고</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 결과 그리드
        cols = st.columns(2)
        
        for i, content in enumerate(st.session_state.generated_contents):
            with cols[i % 2]:
                # 카드 컨테이너
                with st.container():
                    # 헤더
                    st.markdown(f"**버전 {content['id']}** {content['tone']}")
                    
                    # 원고 내용
                    st.markdown("---")
                    
                    # 수정 모드 확인
                    if st.session_state.get(f"editing_{content['id']}", False):
                        edited_text = st.text_area(
                            "원고 수정",
                            value=content['text'],
                            height=200,
                            key=f"edit_content_{content['id']}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 저장", key=f"save_{content['id']}"):
                                # 수정된 내용으로 업데이트
                                for i, c in enumerate(st.session_state.generated_contents):
                                    if c['id'] == content['id']:
                                        st.session_state.generated_contents[i]['text'] = edited_text
                                        break
                                st.session_state[f"editing_{content['id']}"] = False
                                st.success("원고가 수정되었습니다!")
                                st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 취소", key=f"cancel_{content['id']}"):
                                st.session_state[f"editing_{content['id']}"] = False
                                st.rerun()
                    else:
                        st.text_area(
                            "생성된 원고",
                            value=content['text'],
                            height=200,
                            disabled=True,
                            key=f"content_{content['id']}"
                        )
                    
                    # 액션 버튼
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"📋 복사", key=f"copy_{content['id']}"):
                            # 클립보드에 복사하는 더 안전한 방법
                            import pyperclip
                            import platform
                            
                            try:
                                pyperclip.copy(content['text'])
                                # 운영체제별 메시지
                                if platform.system() == "Darwin":  # macOS
                                    success_msg = "✅ 원고가 클립보드에 복사되었습니다! **Cmd+V**로 붙여넣기하세요."
                                elif platform.system() == "Windows":  # Windows
                                    success_msg = "✅ 원고가 클립보드에 복사되었습니다! **Ctrl+V**로 붙여넣기하세요."
                                else:  # Linux, 기타
                                    success_msg = "✅ 원고가 클립보드에 복사되었습니다! **Ctrl+V**로 붙여넣기하세요."
                                
                                st.success(success_msg)
                            except:
                                # pyperclip이 안 되면 JavaScript 방법 시도
                                st.markdown(f"""
                                <script>
                                async function copyToClipboard() {{
                                    const text = `{content['text'].replace('`', '\\`').replace('$', '\\$').replace('\\', '\\\\')}`;
                                    
                                    try {{
                                        if (navigator.clipboard && window.isSecureContext) {{
                                            await navigator.clipboard.writeText(text);
                                            console.log('Clipboard API로 복사 성공');
                                        }} else {{
                                            // 대체 방법
                                            const textArea = document.createElement('textarea');
                                            textArea.value = text;
                                            textArea.style.position = 'fixed';
                                            textArea.style.opacity = '0';
                                            document.body.appendChild(textArea);
                                            textArea.focus();
                                            textArea.select();
                                            document.execCommand('copy');
                                            document.body.removeChild(textArea);
                                            console.log('execCommand로 복사 성공');
                                        }}
                                    }} catch (err) {{
                                        console.error('복사 실패:', err);
                                    }}
                                }}
                                copyToClipboard();
                                </script>
                                """, unsafe_allow_html=True)
                                
                                # 운영체제별 대체 메시지
                                if platform.system() == "Darwin":  # macOS
                                    fallback_msg = "✅ 복사를 시도했습니다! **Cmd+V**로 붙여넣기해보세요."
                                elif platform.system() == "Windows":  # Windows
                                    fallback_msg = "✅ 복사를 시도했습니다! **Ctrl+V**로 붙여넣기해보세요."
                                else:  # Linux, 기타
                                    fallback_msg = "✅ 복사를 시도했습니다! **Ctrl+V**로 붙여넣기해보세요."
                                
                                st.success(fallback_msg)
                    
                    with col_btn2:
                        if st.button(f"✏️ 수정", key=f"edit_{content['id']}"):
                            st.session_state[f"editing_{content['id']}"] = True
                            st.rerun()
                    
                    
                    st.markdown("")  # 간격
        
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

if __name__ == "__main__":
    main()
