import streamlit as st

from services import generate_viral_copy, user_feedback
from utils.validators import validate_input_form
from ..components.ui_helpers import show_error_message

# 입력 폼 표시
def show_input_form():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # 입력값 초기화/복원 로직
    if hasattr(st.session_state, 'clear_inputs') and st.session_state.clear_inputs:
        # 새로운 원고 생성 시 모든 입력값 초기화
        st.session_state.clear_inputs = False
        default_values = {}
        default_emphasis = []
    elif hasattr(st.session_state, 'last_input_data') and st.session_state.last_input_data:
        # 입력 화면으로 돌아갈 때는 세션에 저장된 바로 전 입력값 복원
        default_values = st.session_state.last_input_data.copy()
        
        # 강조사항 복원 로직
        default_emphasis = []
        emphasis_fields = ['event', 'card', 'coupon', 'keyword', 'etc']
        emphasis_mapping = {
            'event': '이벤트',
            'card': '카드 혜택', 
            'coupon': '쿠폰',
            'keyword': '특정 키워드',
            'etc': '기타'
        }
        
        for field in emphasis_fields:
            if default_values.get(field, '').strip():
                default_emphasis.append(emphasis_mapping[field])
    else:
        # 첫 방문이거나 세션 데이터가 없는 경우
        default_values = {}
        default_emphasis = []
    
    # 기본 정보
    st.subheader("📝 기본 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input(
            "상품 아이템 *",
            value=default_values.get('product_name', ''),
            placeholder="예: 나이키 에어맥스",
            help="생성할 상품의 이름을 입력하세요"
        )
    
    with col2:
        price = st.text_input(
            "가격",
            value=default_values.get('price', ''),
            placeholder="예: 89,000원",
            help="상품의 가격을 입력하세요"
        )
    
    # 상품 속성 추가
    product_attribute = st.text_input(
        "상품 속성",
        value=default_values.get('product_attribute', ''),
        placeholder="예: 사이즈 / 색상 / 소재 / 기능",
        help="상품의 주요 특징이나 속성을 입력하세요"
    )
    
    st.divider()
    
    # 타겟 설정
    st.subheader("🎯 타겟 설정")
    
    community = st.selectbox(
        "타겟 커뮤니티 *",
        options=["mam2bebe", "ppomppu", "fmkorea"],
        index=["mam2bebe", "ppomppu", "fmkorea"].index(default_values.get('community', 'mam2bebe')),
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
        '이벤트': '예: 첫 구매 시 추가 5,000원 할인, 무료배송',
        '특정 키워드': '예: 한정수량, 조기품절, 인기상품',
        '카드 혜택': '예: 신한카드 5% 할인, 삼성카드 3만원 적립',
        '기타': '상세 내용을 입력하세요'
    }
    
    # 강조사항 선택
    selected_emphasis = st.multiselect(
        "강조 사항 종류 선택",
        options=emphasis_options,
        default=default_emphasis,
        help="원고에 포함할 강조사항을 선택하세요"
    )
    
    emphasis_details = []
    
    # 선택된 강조사항별 상세 입력
    if selected_emphasis:
        st.markdown("**상세 내용 입력:**")
        for emphasis_type in selected_emphasis:
            with st.expander(f"📌 {emphasis_type}", expanded=True):
                # 강조사항별 기본값 설정
                emphasis_field_mapping = {
                    '이벤트': 'event',
                    '카드 혜택': 'card',
                    '쿠폰': 'coupon',
                    '특정 키워드': 'keyword',
                    '기타': 'etc'
                }
                field_name = emphasis_field_mapping.get(emphasis_type, '')
                default_text = default_values.get(field_name, '') if field_name else ''
                
                emphasis_text = st.text_area(
                    f"{emphasis_type} 상세 내용",
                    value=default_text,
                    placeholder=emphasis_placeholders[emphasis_type],
                    key=f"emphasis_{emphasis_type}",
                    height=100
                )
                if emphasis_text.strip():
                    emphasis_details.append(emphasis_text.strip())
    
    st.divider()
    
    # 베스트 사례
    st.subheader("👍 베스트 사례")
    
    # 베스트 사례를 간단한 방식으로 처리 (안정성을 위해)
    best_case = st.text_area(
        "베스트 사례 원고",
        value=default_values.get('best_case', ''),
        placeholder="좋은 반응을 얻었던 원고 문구나 표현 방식을 자유롭게 입력하세요",
        height=200,
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
                            
                            # 현재 입력 정보를 세션에 저장 (입력 화면으로 돌아갈 때 사용)
                            st.session_state.last_input_data = {
                                'product_name': product_name,
                                'price': price,
                                'product_attribute': product_attribute,
                                'event': emphasis_mapping.get("이벤트", ""),
                                'card': emphasis_mapping.get("카드 혜택", ""),
                                'coupon': emphasis_mapping.get("쿠폰", ""),
                                'keyword': emphasis_mapping.get("특정 키워드", ""),
                                'etc': emphasis_mapping.get("기타", ""),
                                'community': community,
                                'best_case': best_case or ""
                            }
                            
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
    
    # 하단 안내
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 14px;'>* 필수 입력 항목을 모두 작성한 후 원고를 생성하세요</p>",
        unsafe_allow_html=True
    )
