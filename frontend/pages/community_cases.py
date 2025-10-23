import streamlit as st

def show_community_cases_page(user_id: str):
    """커뮤니티별 사례 페이지를 표시합니다."""
    
    # 사이드바 네비게이션
    with st.sidebar:
        # 사용자 정보
        st.markdown("### 👤 사용자 정보")
        st.markdown(f"**팀:** {st.session_state.get('team_name', '')}")
        st.markdown(f"**이름:** {st.session_state.get('user_name', '')}")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", type="secondary", use_container_width=True, key="community_logout"):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # 네비게이션 섹션
        st.markdown("### 🧭 페이지 이동")
        
        # 메인 화면 버튼
        if st.button("🏠 상품 정보 기입", use_container_width=True, key="community_main"):
            st.session_state.current_page = "main"
            st.session_state.show_results = False  # 상품 정보 입력 화면으로 이동
            st.rerun()
        
        # 활동 히스토리 버튼
        if st.button("📊 활동 히스토리", use_container_width=True, key="community_history"):
            st.session_state.current_page = "history"
            st.rerun()
        
        st.divider()
        
        # 피드백 섹션 (맨 아래로 이동)
        st.markdown("### 💬 피드백")
        
        # 피드백 전송 성공 메시지 표시
        if hasattr(st.session_state, 'feedback_sent') and st.session_state.feedback_sent:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.success("🎉 피드백이 전송되었습니다!")
            with col2:
                if st.button("✕", key="close_feedback_msg", help="메시지 닫기", use_container_width=True):
                    st.session_state.feedback_sent = False
                    st.rerun()
        
        feedback_text = st.text_area(
            "서비스 개선을 위한 피드백을 남겨주세요!",
            placeholder="예: 더 다양한 톤의 문구가 필요해요, 특정 키워드 강조 기능이 있었으면 좋겠어요",
            height=100,
            help="여러분의 소중한 의견이 더 나은 서비스로 이어집니다😄",
            key="community_feedback_text"
        )
        
        if st.button("📝 피드백 전송", use_container_width=True, key="community_feedback"):
            if feedback_text.strip():
                try:
                    from services import user_feedback
                    feedback_result = user_feedback(
                        user_id=user_id,
                        feedback_text=feedback_text
                    )
                    
                    if feedback_result:
                        st.session_state.feedback_sent = True
                        st.rerun()
                    else:
                        st.error("피드백 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("피드백 내용을 입력해주세요")
    
    # 메인화면 이동 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 메인화면", key="community_cases_back_button"):
            st.session_state.current_page = "main"
            st.session_state.show_results = False  # 상품 정보 입력 화면으로 이동
            st.rerun()
    
    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>🏘️ 커뮤니티별 사례</h1>
        <p>각 커뮤니티별 성공 사례와 특징을 확인해보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 커뮤니티별 사례 내용
    st.markdown("### 📋 커뮤니티별 특징")
    
    # 커뮤니티 매핑
    community_mapping = {
        "mam2bebe": "맘이베베",
        "fmkorea": "에펨코리아", 
        "ppomppu": "뽐뿌"
    }
    
    # 각 커뮤니티별 정보 표시
    for community_key, community_name in community_mapping.items():
        with st.expander(f"🏘️ {community_name}", expanded=False):
            st.markdown(f"**커뮤니티:** {community_name}")
            
            if community_key == "mam2bebe":
                st.markdown("""
                **특징:**
                - 육아 관련 상품에 특화
                - 엄마들의 실용적인 관점 중시
                - 아이의 안전과 건강을 최우선으로 고려
                - 가성비와 실용성 강조
                
                **성공 사례:**
                - 육아용품, 아동복, 장난감 등
                - "우리 아이를 위한" 접근법
                - 실제 사용 후기와 경험담 공유
                """)
            
            elif community_key == "fmkorea":
                st.markdown("""
                **특징:**
                - 패션, 뷰티, 라이프스타일 중심
                - 트렌드에 민감하고 세련된 감각
                - 브랜드와 디자인에 대한 관심 높음
                - SNS 친화적인 콘텐츠 선호
                
                **성공 사례:**
                - 패션 아이템, 뷰티 제품, 라이프스타일 용품
                - "이거 진짜 예쁘다" 같은 감성적 접근
                - 인스타그램 스타일의 시각적 어필
                """)
            
            elif community_key == "ppomppu":
                st.markdown("""
                **특징:**
                - 할인과 특가 정보에 민감
                - 가성비와 실용성 중시
                - 구체적인 가격 정보 선호
                - 실제 구매 후기와 리뷰 중시
                
                **성공 사례:**
                - 전자제품, 생활용품, 식품 등
                - "이 가격에 이 성능" 접근법
                - 구체적인 할인율과 혜택 정보
                """)
    
    st.divider()
    
    # 사용 팁
    st.markdown("### 💡 활용 팁")
    st.info("""
    **각 커뮤니티의 특성을 파악하고 맞춤형 콘텐츠를 생성하세요!**
    
    1. **맘이베베**: 안전성과 실용성을 강조
    2. **에펨코리아**: 트렌드와 디자인을 어필
    3. **뽐뿌**: 가성비와 할인 혜택을 부각
    """)
