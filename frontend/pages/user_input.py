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
            is_valid, error_msg = validate_input_form(product_name, price, community)
            if is_valid:
                with st.spinner("원고를 생성하고 있습니다..."):
                    # 임시로 원본 generate_content 함수 사용
                    from app import generate_content
                    generated_contents = generate_content(
                        product_name, price, None, None, 
                        community, emphasis_details, best_case
                    )
                    st.session_state.generated_contents = generated_contents
                    st.session_state.current_generate_id = "temp_generate_id"
                    st.session_state.show_results = True
                    st.rerun()
            else:
                show_error_message(error_msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 하단 안내
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 14px;'>* 필수 입력 항목을 모두 작성한 후 원고를 생성하세요</p>",
        unsafe_allow_html=True
    )
