"""
사용자 입력 페이지
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services import generate_viral_copy, user_feedback
from utils.validators import validate_input_form
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
                    try:
                        # 실제 백엔드 서비스 호출
                        # 강조사항을 선택된 항목에 맞게 매핑
                        emphasis_mapping = {
                            "이벤트": "",
                            "카드 혜택": "",
                            "쿠폰": "",
                            "특정 키워드": "",
                            "기타": ""
                        }
                        
                        # 선택된 강조사항에 따라 매핑
                        for i, emphasis_type in enumerate(selected_emphasis):
                            if i < len(emphasis_details):
                                emphasis_mapping[emphasis_type] = emphasis_details[i]
                        
                        product_data = {
                            "product_name": product_name,
                            "price": price or "",
                            "product_attribute": product_attribute or "",
                            "community": community,
                            "event": emphasis_mapping.get("이벤트", ""),
                            "card": emphasis_mapping.get("카드 혜택", ""),
                            "coupon": emphasis_mapping.get("쿠폰", ""),
                            "keyword": emphasis_mapping.get("특정 키워드", ""),
                            "etc": emphasis_mapping.get("기타", ""),
                            "best_case": best_case or ""
                        }
                        
                        result = generate_viral_copy(
                            user_id=st.session_state.user_id,
                            product_data=product_data
                        )
                        
                        if result and result.get("generate_id"):
                            st.session_state.generated_contents = result["generated_contents"]
                            st.session_state.current_generate_id = result.get("generate_id", "temp_id")
                            st.session_state.show_results = True
                            st.success("원고 생성이 완료되었습니다! 🎉")
                            st.rerun()
                        else:
                            st.error(f"원고 생성에 실패했습니다: {result.get('error', '알 수 없는 오류')}")
                    except Exception as e:
                        st.error(f"원고 생성 중 오류가 발생했습니다: {str(e)}")
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
    
    # 하단 안내
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 14px;'>* 필수 입력 항목을 모두 작성한 후 원고를 생성하세요</p>",
        unsafe_allow_html=True
    )
