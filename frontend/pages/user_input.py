"""
사용자 입력 페이지
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# from services import generate_viral_copy  # 임시 주석처리
from utils import validate_input_form
from ..components.ui_helpers import show_error_message


def generate_temp_content(product_name, price, community, emphasis_details, best_case=""):
    """임시 콘텐츠 생성 함수 (백엔드 연결 전)"""
    
    # 커뮤니티별 톤 조정
    community_tones = {
        'mam2bebe': ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'],
        'ppomppu': ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'],
        'fmkorea': ['정보 전달형', '후기형', '친근한 톤', '유머러스한 톤']
    }
    
    tones = community_tones.get(community, ['친근한 톤', '정보 전달형', '후기형', '유머러스한 톤'])
    
    # 강조사항 텍스트 생성
    emphasis_text = '\n'.join([f"• {detail}" for detail in emphasis_details]) if emphasis_details else ""
    
    # 커뮤니티명 변환
    community_names = {
        'mam2bebe': '맘이베베',
        'ppomppu': '뽐뿌',
        'fmkorea': '에펨코리아'
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


def show_input_form():
    """입력 폼 표시"""
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
            "가격",
            placeholder="예: 89,000원",
            help="상품의 가격을 입력하세요"
        )
    
    # 상품 속성 추가
    product_attribute = st.text_input(
        "상품 속성",
        placeholder="예: 방풍, 방수, 가벼움, 통기성 좋음",
        help="상품의 주요 특징이나 속성을 입력하세요"
    )
    
    st.divider()
    
    # 타겟 설정
    st.subheader("🎯 타겟 설정")
    
    community = st.selectbox(
        "타겟 커뮤니티 *",
        options=["mam2bebe", "ppomppu", "fmkorea"],
        format_func=lambda x: {
            "mam2bebe": "맘이베베",
            "ppomppu": "뽐뿌",
            "fmkorea": "에펨코리아"
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
            is_valid, error_msg = validate_input_form(product_name, community)
            if is_valid:
                with st.spinner("원고를 생성하고 있습니다..."):
                    # 임시 하드코딩된 콘텐츠 생성 (백엔드 연결 전)
                    generated_contents = generate_temp_content(
                        product_name, price, community, emphasis_details, best_case
                    )
                    st.session_state.generated_contents = generated_contents
                    st.session_state.current_generate_id = "temp_generate_id"
                    st.session_state.show_results = True
                    st.rerun()
            else:
                show_error_message(error_msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 피드백 섹션
    st.markdown("---")
    st.markdown("### 💬 피드백")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        feedback_text = st.text_area(
            "서비스 개선을 위한 피드백을 남겨주세요",
            placeholder="예: 더 다양한 톤의 문구가 필요해요, 특정 키워드 강조 기능이 있었으면 좋겠어요",
            height=100,
            help="여러분의 소중한 의견이 더 나은 서비스로 이어집니다"
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
    
    # 하단 안내
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 14px;'>* 필수 입력 항목을 모두 작성한 후 원고를 생성하세요</p>",
        unsafe_allow_html=True
    )
