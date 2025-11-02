import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.get_logger import get_logger

# 로거 초기화
logger = get_logger()

def load_community_data():
    """커뮤니티 데이터를 로드하고 분석합니다."""
    try:
        # CSV 파일 로드
        df = pd.read_csv('community_data.csv')
        
        # 데이터 정리 (int 형으로 변환)
        df['view_cnt'] = pd.to_numeric(df['view_cnt'], errors='coerce').fillna(0).astype(int)
        df['like_cnt'] = pd.to_numeric(df['like_cnt'], errors='coerce').fillna(0).astype(int)
        df['comment_cnt'] = pd.to_numeric(df['comment_cnt'], errors='coerce').fillna(0).astype(int)
        
        # 날짜 컬럼 변환 및 주차 계산 (여러 형식 지원)
        df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce')
        # 날짜 변환이 실패한 행 제거 (NaT인 경우)
        df = df.dropna(subset=['created_at'])
        df['week'] = df['created_at'].apply(get_week_number)
        
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

def get_week_number(date):
    """날짜를 기반으로 주차를 계산합니다."""
    try:
        # 10월 주차 계산 (자동 계산)
        # 10월 5주차: 10월 26일 ~ 11월 2일 (11월 1일, 2일 포함)
        oct_13 = datetime(2025, 10, 13)
        oct_20 = datetime(2025, 10, 20)
        oct_26 = datetime(2025, 10, 26)
        nov_2_end = datetime(2025, 11, 2, 23, 59, 59)  # 11월 2일 끝까지
        
        if date < oct_13:
            return "10월 2주차 이전"
        elif oct_13 <= date < oct_20:
            return "10월 3주차"
        elif oct_20 <= date < oct_26:
            return "10월 4주차"
        elif oct_26 <= date <= nov_2_end:
            return "10월 5주차"
        else:
            return "11월 이후"
    except:
        return "알 수 없음"

def get_top_cases_by_community(df, community, sort_by='composite_score', top_n=100, week_filter=None, category_filter=None, own_company_filter=None):
    """커뮤니티별 상위 사례를 반환합니다."""
    community_data = df[df['channel'] == community].copy()
    
    if community_data.empty:
        return pd.DataFrame()
    
    # 주차 필터링
    if week_filter and week_filter != "전체":
        community_data = community_data[community_data['week'] == week_filter]
    
    # 카테고리 필터링
    if category_filter and category_filter != "전체":
        community_data = community_data[community_data['category'] == category_filter]
    
    # 회사 필터링
    if own_company_filter and own_company_filter != "전체":
        if own_company_filter == "롯데on":
            community_data = community_data[community_data['own_company'] == 1]
        elif own_company_filter == "타회사":
            community_data = community_data[community_data['own_company'] == 0]
    
    if community_data.empty:
        return pd.DataFrame()
    
    # 정렬 기준에 따라 정렬
    if sort_by == 'view_cnt':
        top_cases = community_data.nlargest(top_n, 'view_cnt')
    elif sort_by == 'like_cnt':
        top_cases = community_data.nlargest(top_n, 'like_cnt')
    elif sort_by == 'comment_cnt':
        top_cases = community_data.nlargest(top_n, 'comment_cnt')
    else:
        top_cases = community_data.nlargest(top_n, 'view_cnt')  # 기본값을 조회수로 설정
    
    return top_cases

def show_community_tab(df, channel, display_name):
    """커뮤니티별 탭 내용을 표시합니다."""
    # 커뮤니티별 좋아요/추천수 표시 설정
    like_label = "👍 좋아요" if channel == "mam2bebe" else "👍 추천수"
    
    # 정렬 기준 선택 (커뮤니티별 기본값 설정)
    sort_options = {
        like_label: 'like_cnt', 
        '👀 조회수': 'view_cnt',
        '💬 댓글수': 'comment_cnt'
    }
    
    # 커뮤니티별 기본 정렬 설정
    default_sort_index = 1 if channel == "mam2bebe" else 2  # 맘이베베: 조회수, 나머지: 댓글수
    
    # 필터링 옵션
    community_data = df[df['channel'] == channel]
    
    # 주차 옵션
    week_options = ["전체"] + sorted(community_data['week'].unique().tolist())
    
    # 카테고리 옵션
    category_options = ["전체"] + sorted(community_data['category'].unique().tolist())
    
    # 회사 옵션
    company_options = ["전체", "롯데on", "타회사"]
    
    # 필터링 UI
    st.markdown(f"### {display_name} 트렌드 모니터")
    
    # 필터링 컨트롤
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        week_filter = st.selectbox(
            "📅 주차:",
            options=week_options,
            index=0,
            key=f"week_{channel}"
        )
    
    with col2:
        category_filter = st.selectbox(
            "🏷️ 카테고리:",
            options=category_options,
            index=0,
            key=f"category_{channel}"
        )
    
    with col3:
        sort_by = st.selectbox(
            "📊 정렬 기준:",
            options=list(sort_options.keys()),
            index=default_sort_index,
            key=f"sort_{channel}"
        )
    
    with col4:
        own_company_filter = st.selectbox(
            "🏢 회사:",
            options=company_options,
            index=0,
            key=f"company_{channel}"
        )
    
    with col5:
        # 필터링된 데이터 개수 표시
        filtered_data = community_data.copy()
        if week_filter != "전체":
            filtered_data = filtered_data[filtered_data['week'] == week_filter]
        if category_filter != "전체":
            filtered_data = filtered_data[filtered_data['category'] == category_filter]
        if own_company_filter != "전체":
            if own_company_filter == "롯데on":
                filtered_data = filtered_data[filtered_data['own_company'] == 1]
            elif own_company_filter == "타회사":
                filtered_data = filtered_data[filtered_data['own_company'] == 0]
        
        st.metric("📈 총 사례 수", f"{len(filtered_data)}개")
    
    # 선택된 정렬 기준으로 데이터 가져오기 (최대 100개)
    sort_key = sort_options[sort_by]
    top_cases = get_top_cases_by_community(df, channel, sort_key, 100, week_filter, category_filter, own_company_filter)
    
    if top_cases.empty:
        # 필터링 조건에 따른 메시지
        filter_msg = []
        if week_filter != "전체":
            filter_msg.append(f"주차: {week_filter}")
        if category_filter != "전체":
            filter_msg.append(f"카테고리: {category_filter}")
        
        if filter_msg:
            st.warning(f"선택한 조건 ({', '.join(filter_msg)})에 해당하는 {display_name} 데이터가 없습니다.")
        else:
            st.warning(f"{display_name} 데이터가 없습니다.")
        return
    
    # 페이지네이션 설정
    items_per_page = 10
    total_items = len(top_cases)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # 현재 페이지 상태 초기화
    if f'current_page_{channel}' not in st.session_state:
        st.session_state[f'current_page_{channel}'] = 1
    
    # 현재 페이지에 해당하는 데이터 추출
    current_page = st.session_state[f'current_page_{channel}']
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_cases = top_cases.iloc[start_idx:end_idx]
    
    # 현재 페이지 정보 표시
    st.info(f"📊 총 {total_items}개 사례 중 {start_idx + 1}-{end_idx}번째 사례를 표시합니다.")
    
    for idx, (_, case) in enumerate(current_cases.iterrows(), start_idx + 1):
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
                        # 베스트 사례 적용 로그 기록
                        logger.info(f"BEST_CASE_APPLY - user_id: {st.session_state.user_id}, case_id: {str(case.get('id', idx))}, community: {channel}")
                        
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
            
            # 카테고리, 주차, 회사 정보를 같은 행에 표시
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.markdown(f"**카테고리:** {case['category']}")
            with col_info2:
                st.markdown(f"**주차:** {case['week']}")
            with col_info3:
                company_name = "롯데on" if case.get('own_company', 0) == 1 else "타회사"
                st.markdown(f"**회사:** {company_name}")
            
            st.markdown(f"**작성일:** {case['created_at'].strftime('%Y-%m-%d %H:%M')}")
            
            # URL 정보 표시 (있는 경우)
            if pd.notna(case.get('url')) and str(case.get('url')).strip():
                st.markdown(f"**🔗 원문 링크:** [바로가기]({case['url']})")
            
            # 전체 내용 표시 (미리보기 제거하고 전체 내용을 바로 표시)
            st.markdown("**내용:**")
            st.markdown(f"```\n{case['content']}\n```")
    
    # 페이지네이션 컨트롤 (히스토리 화면과 동일한 구조)
    if total_pages > 1:
        st.markdown("---")
        
        # 페이지네이션을 중앙 정렬된 컨테이너로 표시
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; padding: 1rem 0;">
            <span style="padding: 0.5rem 1rem; font-weight: bold; color: #495057; background: #f8f9fa; border-radius: 6px; border: 1px solid #dee2e6;">
                페이지 {st.session_state[f'current_page_{channel}']} / {total_pages}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 버튼들을 중앙 정렬
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col1:
            if st.button("⏮️ 처음", key=f"first_{channel}", help="첫 페이지로 이동", use_container_width=True):
                st.session_state[f'current_page_{channel}'] = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ 이전", key=f"prev_{channel}", help="이전 페이지로 이동", use_container_width=True):
                if st.session_state[f'current_page_{channel}'] > 1:
                    st.session_state[f'current_page_{channel}'] -= 1
                    st.rerun()
        
        with col3:
            st.empty()  # 빈 공간
        
        with col4:
            if st.button("다음 ▶️", key=f"next_{channel}", help="다음 페이지로 이동", use_container_width=True):
                if st.session_state[f'current_page_{channel}'] < total_pages:
                    st.session_state[f'current_page_{channel}'] += 1
                    st.rerun()
        
        with col5:
            if st.button("끝 ⏭️", key=f"last_{channel}", help="마지막 페이지로 이동", use_container_width=True):
                st.session_state[f'current_page_{channel}'] = total_pages
                st.rerun()

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
    
    # 사이드바는 main.py에서 통합 관리하므로 제거
    
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
    st.subheader("🏆 커뮤니티별 베스트 사례 (페이지별 10개)")
    
    # 필터링 가이드와 베스트 사례 안내
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
                    height: 280px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 1.5rem;">
                    🔍 필터링 옵션
                </h4>
                <div style="display: flex; justify-content: space-between; gap: 0.5rem; margin-bottom: 1.5rem; margin-top: 3rem; align-items: center;">
                    <span style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                                color: #1e40af; 
                                padding: 0.75rem 1.25rem; 
                                border-radius: 20px; 
                                font-size: 1rem; 
                                font-weight: 600;
                                box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2);
                                border: 2px solid #3b82f6;
                                flex: 1;
                                text-align: center;">
                        📅 주차별
                    </span>
                    <span style="background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); 
                                color: #7c3aed; 
                                padding: 0.75rem 1.25rem; 
                                border-radius: 20px; 
                                font-size: 1rem; 
                                font-weight: 600;
                                box-shadow: 0 2px 4px rgba(124, 58, 237, 0.2);
                                border: 2px solid #a855f7;
                                flex: 1;
                                text-align: center;">
                        🏷️ 카테고리
                    </span>
                    <span style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                                color: #166534; 
                                padding: 0.75rem 1.25rem; 
                                border-radius: 20px; 
                                font-size: 1rem; 
                                font-weight: 600;
                                box-shadow: 0 2px 4px rgba(22, 101, 52, 0.2);
                                border: 2px solid #22c55e;
                                flex: 1;
                                text-align: center;">
                        📊 정렬기준
                    </span>
                </div>
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
                    height: 280px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0; color: #92400e; font-weight: 600; font-size: 1.5rem;">
                    🎯 베스트 사례 활용법
                </h4>
                <div style="text-align: left; margin-bottom: 0.3rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                        <span style="background: #f59e0b; color: white; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; margin-right: 0.5rem; font-weight: bold;">1</span>
                        <span style="font-size: 0.8rem; color: #92400e; font-weight: 500;">필터링으로 원하는 사례 찾기</span>
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
                    ✨ <strong>팁:</strong> 주차별/카테고리별로 성공 사례를 분석해보세요!
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