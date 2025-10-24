import streamlit as st
import pandas as pd
import numpy as np

def load_community_data():
    """커뮤니티 데이터를 로드하고 분석합니다."""
    try:
        # CSV 파일 로드
        df = pd.read_csv('community_data.csv')
        
        # 데이터 정리
        df['view_cnt'] = pd.to_numeric(df['view_cnt'], errors='coerce').fillna(0)
        df['like_cnt'] = pd.to_numeric(df['like_cnt'], errors='coerce').fillna(0)
        df['comment_cnt'] = pd.to_numeric(df['comment_cnt'], errors='coerce').fillna(0)
        
        # 종합 지표 계산 (가중 평균)
        # 조회수 40%, 좋아요 35%, 댓글수 25% 가중치 적용
        df['composite_score'] = (
            df['view_cnt'] * 0.4 + 
            df['like_cnt'] * 0.35 + 
            df['comment_cnt'] * 0.25
        )
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

def get_top_cases_by_community(df, community, sort_by='composite_score', top_n=10):
    """커뮤니티별 상위 사례를 반환합니다."""
    community_data = df[df['channel'] == community].copy()
    
    if community_data.empty:
        return pd.DataFrame()
    
    # 정렬 기준에 따라 정렬
    if sort_by == 'composite_score':
        top_cases = community_data.nlargest(top_n, 'composite_score')
    elif sort_by == 'like_cnt':
        top_cases = community_data.nlargest(top_n, 'like_cnt')
    elif sort_by == 'view_cnt':
        top_cases = community_data.nlargest(top_n, 'view_cnt')
    elif sort_by == 'comment_cnt':
        top_cases = community_data.nlargest(top_n, 'comment_cnt')
    else:
        top_cases = community_data.nlargest(top_n, 'composite_score')
    
    return top_cases

def show_community_tab(df, channel, display_name):
    """커뮤니티별 탭 내용을 표시합니다."""
    # 커뮤니티별 좋아요/추천수 표시 설정
    like_label = "👍 좋아요" if channel == "mam2bebe" else "👍 추천수"
    
    # 정렬 기준 선택
    sort_options = {
        '📊 종합지표': 'composite_score',
        like_label: 'like_cnt', 
        '👀 조회수': 'view_cnt',
        '💬 댓글수': 'comment_cnt'
    }
    
    # 정렬 기준 선택 UI
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {display_name}")
    
    with col2:
        sort_by = st.selectbox(
            "정렬 기준:",
            options=list(sort_options.keys()),
            index=0,  # 기본값: 종합지표
            key=f"sort_{channel}"
        )
    
    # 선택된 정렬 기준으로 데이터 가져오기
    sort_key = sort_options[sort_by]
    top_cases = get_top_cases_by_community(df, channel, sort_key, 10)
    
    if top_cases.empty:
        st.warning(f"{display_name} 데이터가 없습니다.")
        return
    
    for idx, (_, case) in enumerate(top_cases.iterrows(), 1):
        with st.expander(f"#{idx} {case['title'][:50]}{'...' if len(case['title']) > 50 else ''}", expanded=False):
            # 기본 정보와 베스트 사례 적용 버튼을 같은 행에 배치
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                st.metric("👀 조회수", f"{case['view_cnt']:,}")
            with col2:
                # 커뮤니티별로 좋아요/추천수 표시
                if channel == "mam2bebe":
                    st.metric("👍 좋아요", f"{case['like_cnt']:,}")
                else:
                    st.metric("👍 추천수", f"{case['like_cnt']:,}")
            with col3:
                st.metric("💬 댓글", f"{case['comment_cnt']:,}")
            with col4:
                # 베스트 사례 적용 버튼을 맨 오른쪽에 배치
                if st.button(f"📋 베스트 사례 적용", key=f"apply_case_{channel}_{idx}", use_container_width=True):
                    # 확인 상태로 변경
                    st.session_state[f'show_confirm_{channel}_{idx}'] = True
                    st.rerun()
            
            # 베스트 사례 적용 확인 섹션
            if st.session_state.get(f'show_confirm_{channel}_{idx}', False):
                st.markdown("---")
                st.markdown("### ⭐️ 베스트 사례 적용 확인")
                st.markdown("**상품 정보 기입 화면에 적용하시겠습니까?**")
                
                # 확인/취소 버튼
                col_confirm1, col_confirm2 = st.columns(2)
                
                with col_confirm1:
                    if st.button("✅ 확인", key=f"confirm_apply_{channel}_{idx}", use_container_width=True, type="primary"):
                        # 베스트 사례를 세션에 저장하고 메인 페이지로 이동
                        st.session_state.best_case = case['content']
                        st.session_state.current_page = "main"
                        st.session_state.show_results = False
                        st.session_state[f'show_confirm_{channel}_{idx}'] = False
                        st.success("✅ 베스트 사례가 적용되었습니다! 상품 정보 기입 화면으로 이동합니다.")
                        st.rerun()
                
                with col_confirm2:
                    if st.button("❌ 취소", key=f"cancel_apply_{channel}_{idx}", use_container_width=True):
                        st.session_state[f'show_confirm_{channel}_{idx}'] = False
                        st.rerun()
            
            st.markdown("---")
            
            # 제목과 내용
            st.markdown(f"**제목:** {case['title']}")
            st.markdown(f"**카테고리:** {case['category']}")
            st.markdown(f"**작성일:** {case['created_at']}")
            
            # 전체 내용 표시 (미리보기 제거하고 전체 내용을 바로 표시)
            st.markdown("**내용:**")
            st.markdown(f"```\n{case['content']}\n```")

def show_community_cases_page(user_id: str):
    """커뮤니티별 사례 페이지를 표시합니다."""
    
    # 사이드바 폭 조정 CSS
    st.markdown("""
    <style>
    .css-1d391kg {
        width: 300px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바 네비게이션
    with st.sidebar:
        # 사용자 정보
        st.markdown("### 👤 사용자 정보")
        st.markdown(f"**팀:** {st.session_state.get('team_name', '')}")
        st.markdown(f"**사용자:** {st.session_state.get('user_name', '')}")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", key="community_logout"):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # 페이지 이동 버튼들
        st.markdown("### 🧭 페이지 이동")
        
        # 메인 화면 버튼
        if st.button("🏠 상품 정보 기입", use_container_width=True, key="community_to_main"):
            st.session_state.current_page = "main"
            st.session_state.show_results = False
            st.rerun()
        
        # 활동 히스토리 버튼
        if st.button("📊 활동 히스토리", use_container_width=True, key="community_to_history"):
            st.session_state.current_page = "history"
            st.rerun()
        
        st.divider()
        
        # 피드백 섹션 (맨 아래로 이동)
        st.markdown("### 💬 피드백")
        
        # 피드백 전송 성공 메시지 표시
        if hasattr(st.session_state, 'feedback_sent_community') and st.session_state.feedback_sent_community:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.success("🎉 피드백이 전송되었습니다!")
            with col2:
                if st.button("✕", key="close_feedback_community", help="메시지 닫기", use_container_width=True):
                    st.session_state.feedback_sent_community = False
                    st.rerun()
        
        feedback_text = st.text_area(
            "서비스 개선을 위한 피드백을 남겨주세요!",
            placeholder="개선사항이나 의견을 자유롭게 작성해주세요",
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
                        st.session_state.feedback_sent_community = True
                        st.rerun()
                    else:
                        st.error("피드백 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("피드백 내용을 입력해주세요")
    
    # 메인 콘텐츠
    # 뒤로가기 버튼과 제목을 같은 줄에 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← 메인화면", key="community_back_to_main"):
            st.session_state.current_page = "main"
            st.session_state.show_results = False
            st.rerun()
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏘️ 커뮤니티별 베스트 사례</h1>", unsafe_allow_html=True)
    
    with col3:
        st.empty()  # 빈 공간
    
    st.markdown("---")
    
    # 데이터 로드
    df = load_community_data()
    
    if df.empty:
        st.error("데이터를 불러올 수 없습니다.")
        return
    
    # 커뮤니티별 베스트 사례
    st.subheader("🏆 커뮤니티별 베스트 사례 (Top 10)")
    
    # 정렬 기준 설명과 베스트 사례 안내
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    text-align: center; 
                    margin: 1.5rem 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e2e8f0;
                    height: 240px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 1.1rem;">
                    📊 정렬 기준
                </h4>
                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;">
                    <span style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                                color: #1e40af; 
                                padding: 0.5rem 1rem; 
                                border-radius: 20px; 
                                font-size: 0.9rem; 
                                font-weight: 500;
                                box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2);
                                border: 2px solid #3b82f6;">
                        📈 종합지표
                    </span>
                    <span style="background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); 
                                color: #7c3aed; 
                                padding: 0.5rem 1rem; 
                                border-radius: 20px; 
                                font-size: 0.9rem; 
                                font-weight: 500;
                                box-shadow: 0 2px 4px rgba(124, 58, 237, 0.2);
                                border: 2px solid #a855f7;">
                        👍 좋아요/추천
                    </span>
                    <span style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                                color: #166534; 
                                padding: 0.5rem 1rem; 
                                border-radius: 20px; 
                                font-size: 0.9rem; 
                                font-weight: 500;
                                box-shadow: 0 2px 4px rgba(22, 101, 52, 0.2);
                                border: 2px solid #22c55e;">
                        👀 조회수
                    </span>
                    <span style="background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%); 
                                color: #c2410c; 
                                padding: 0.5rem 1rem; 
                                border-radius: 20px; 
                                font-size: 0.9rem; 
                                font-weight: 500;
                                box-shadow: 0 2px 4px rgba(194, 65, 12, 0.2);
                                border: 2px solid #f97316;">
                        💬 댓글수
                    </span>
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.8); 
                        padding: 0.75rem; 
                        border-radius: 8px; 
                        border: 1px solid #e2e8f0;">
                <p style="margin: 0; font-size: 0.85rem; color: #64748b; font-weight: 500;">
                    💡 <strong>종합지표</strong> = 조회수 40% + 좋아요 35% + 댓글수 25%
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    text-align: center; 
                    margin: 1.5rem 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    border: 1px solid #f59e0b;
                    height: 240px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0; color: #92400e; font-weight: 600; font-size: 1.1rem;">
                    🎯 베스트 사례 활용법
                </h4>
                <div style="text-align: left; margin-bottom: 0.3rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                        <span style="background: #f59e0b; color: white; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; margin-right: 0.5rem; font-weight: bold;">1</span>
                        <span style="font-size: 0.8rem; color: #92400e; font-weight: 500;">원하는 사례를 찾아보세요</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                        <span style="background: #f59e0b; color: white; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; margin-right: 0.5rem; font-weight: bold;">2</span>
                        <span style="font-size: 0.8rem; color: #92400e; font-weight: 500;">📋 베스트 사례 적용 버튼 클릭</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span style="background: #f59e0b; color: white; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; margin-right: 0.5rem; font-weight: bold;">3</span>
                        <span style="font-size: 0.8rem; color: #92400e; font-weight: 500;">자동으로 입력 폼에 적용됩니다</span>
                    </div>
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.8); 
                        padding: 0.75rem; 
                        border-radius: 8px; 
                        border: 1px solid #f59e0b;">
                <p style="margin: 0; font-size: 0.85rem; color: #92400e; font-weight: 500;">
                    ✨ <strong>팁:</strong> 성공한 사례의 문구를 참고하여 더 효과적인 원고를 만들어보세요!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 탭으로 커뮤니티별 사례 표시
    tab1, tab2, tab3 = st.tabs(["👩‍🍼 맘이베베", "🅿 뽐뿌", "🅵 에펨코리아"])
    
    with tab1:
        show_community_tab(df, 'mam2bebe', '맘이베베')
    
    with tab2:
        show_community_tab(df, 'ppomppu', '뽐뿌')
    
    with tab3:
        show_community_tab(df, 'fmkorea', '에펨코리아')