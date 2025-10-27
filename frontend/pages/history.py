import streamlit as st
from datetime import datetime, timezone, timedelta
from services.user_service import get_user_history
from database.crud import get_user_contents, get_user_adoption_count, get_user_preferred_tone, get_content_adopted_tones
from utils.get_logger import get_logger

# 로거 초기화
logger = get_logger()

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

def format_korean_time(time_str):
    """데이터베이스 시간을 한국 시간으로 포맷팅합니다."""
    try:
        # UTC 시간으로 파싱 (데이터베이스에 저장된 시간이 UTC라고 가정)
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        # 한국 시간으로 변환
        kst_time = dt.astimezone(KST)
        return kst_time.strftime("%Y-%m-%d %H:%M")
    except:
        # 파싱 실패 시 원본 반환
        return time_str[:16]

def show_history_page(user_id: str):
    """활동 히스토리 페이지를 표시합니다."""
    
    # 사이드바는 main.py에서 통합 관리하므로 제거
    
    # 메인화면 이동 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 메인화면", key="history_back_button"):
            st.session_state.current_page = "main"
            st.session_state.show_results = False  # 상품 정보 입력 화면으로 이동
            st.rerun()
    
    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>📊 활동 히스토리</h1>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 사용자 히스토리 데이터 조회
        history_data = get_user_history(user_id, limit=50)
        
        # 커뮤니티 매핑
        community_mapping = {
            "mam2bebe": "맘이베베",
            "fmkorea": "에펨코리아", 
            "ppomppu": "뽐뿌"
        }
        
        # 채택 횟수 및 선호 톤 조회
        adoption_count = get_user_adoption_count(user_id)
        preferred_tone = get_user_preferred_tone(user_id)
        
        # 통계 정보 표시 (4개로 정리)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📝 총 생성 횟수",
                value=history_data["total_generations"],
                help="지금까지 생성 요청한 총 횟수 (재생성 포함)"
            )
        
        with col2:
            st.metric(
                label="✅ 채택 횟수",
                value=adoption_count,
                help="복사 버튼을 클릭한 총 횟수"
            )
        
        with col3:
            # 가장 많이 채택한 톤 (실제 데이터 기반)
            if preferred_tone:
                st.metric(
                    label="🎭 선호 톤",
                    value=preferred_tone,
                    help="가장 많이 채택한 톤"
                )
            else:
                st.metric(
                    label="🎭 선호 톤",
                    value="없음",
                    help="가장 많이 채택한 톤"
                )
        
        with col4:
            # 가장 많이 사용한 커뮤니티 계산 (매핑된 이름으로 표시)
            communities = [gen.get("community", "") for gen in history_data["generations"]]
            if communities:
                most_used_community = max(set(communities), key=communities.count)
                display_name = community_mapping.get(most_used_community, most_used_community)
                st.metric(
                    label="🏘️ 선호 커뮤니티",
                    value=display_name,
                    help="가장 많이 사용한 커뮤니티"
                )
            else:
                st.metric(
                    label="🏘️ 선호 커뮤니티",
                    value="없음",
                    help="아직 생성 기록이 없습니다"
                )
        
        st.divider()
        
        # 생성 내역 게시판
        st.markdown("### 📋 생성 내역")
        
        # 페이지네이션 설정
        if 'history_page' not in st.session_state:
            st.session_state.history_page = 0
        
        items_per_page = 10
        start_idx = st.session_state.history_page * items_per_page
        end_idx = start_idx + items_per_page
        
        # 생성 히스토리만 표시 (피드백 제외)
        generations = history_data["generations"]
        
        if generations:
            # 시간순 정렬 (최신순)
            generations.sort(key=lambda x: x['created_at'], reverse=True)
            
            # 현재 페이지에 해당하는 데이터만 표시
            current_page_data = generations[start_idx:end_idx]
            total_pages = (len(generations) + items_per_page - 1) // items_per_page
            
            # 생성 내역 게시판 표시
            for i, gen in enumerate(current_page_data):
                # 커뮤니티 매핑된 이름과 이모티콘으로 표시
                community_display = community_mapping.get(gen.get('community', ''), gen.get('community', ''))
                
                # 커뮤니티별 이모티콘 매핑
                community_icons = {
                    '맘이베베': '👩‍🍼',
                    '뽐뿌': '🅿',
                    '에펨코리아': '🅵'
                }
                
                community_icon = community_icons.get(community_display, '🏘️')
                
                # 제목 순서 변경: 커뮤니티 → 상품명 → 날짜
                # 한국 시간으로 포맷팅
                formatted_time = format_korean_time(gen['created_at'])
                with st.expander(f"{community_icon} {community_display} | 🛍️ {gen['product_name']} | 📅 {formatted_time}", expanded=False):
                    # 재생성 여부 확인 (generation_type으로 판단)
                    generation_type = gen.get('generation_type', 'viral_copy')
                    is_regenerated = generation_type == 'regenerate'
                    
                    # 입력 정보와 재생성 여부를 같은 줄에 배치
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # 입력 정보 표시 (모든 입력 데이터)
                        product_info = gen.get('product_info', {})
                        if product_info:
                            st.markdown("### 📋 입력 정보")
                            
                            # 기본 정보 카드
                            basic_info_items = []
                            if product_info.get('product_name'):
                                basic_info_items.append(f"🛍️ 상품명: {product_info['product_name']}")
                            if product_info.get('price'):
                                basic_info_items.append(f"💰 가격: {product_info['price']}")
                            if product_info.get('product_attribute'):
                                basic_info_items.append(f"🏷️ 상품속성: {product_info['product_attribute']}")
                            
                            if basic_info_items:
                                st.markdown(f"""
                                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #28a745;">
                                    <div style="color: #495057; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: bold;">
                                        📝 기본 정보
                                    </div>
                                    <div style="color: #212529; line-height: 1.6;">
                                        {chr(10).join(basic_info_items)}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # 강조사항 카드
                            emphasis_items = []
                            if product_info.get('event'):
                                emphasis_items.append(f"🎉 이벤트: {product_info['event']}")
                            if product_info.get('card'):
                                emphasis_items.append(f"💳 카드 혜택: {product_info['card']}")
                            if product_info.get('coupon'):
                                emphasis_items.append(f"🎫 쿠폰: {product_info['coupon']}")
                            if product_info.get('keyword'):
                                emphasis_items.append(f"🔑 키워드: {product_info['keyword']}")
                            if product_info.get('etc'):
                                emphasis_items.append(f"📌 기타: {product_info['etc']}")
                            
                            if emphasis_items:
                                st.markdown(f"""
                                <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #ffc107;">
                                    <div style="color: #495057; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: bold;">
                                        ⭐ 강조사항
                                    </div>
                                    <div style="color: #212529; line-height: 1.6;">
                                        {chr(10).join(emphasis_items)}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # 베스트사례 카드
                            if product_info.get('best_case'):
                                st.markdown(f"""
                                <div style="background-color: #d1ecf1; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #17a2b8;">
                                    <div style="color: #495057; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: bold;">
                                        👍 베스트사례
                                    </div>
                                    <div style="color: #212529; line-height: 1.6; font-style: italic;">
                                        "{product_info['best_case']}"
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.divider()
                    
                    with col2:
                        # 재생성 여부 배지와 불러오기 버튼을 가로로 나란히 배치
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="background-color: {'#e3f2fd' if is_regenerated else '#e8f5e8'}; 
                                       color: {'#1976d2' if is_regenerated else '#2e7d32'}; 
                                       padding: 0.5rem 1rem; border-radius: 12px; font-size: 0.9rem; font-weight: bold; text-align: center; flex: 1;">
                                {'🔄 재생성' if is_regenerated else '✨ 신규생성'}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 복사한 톤 정보 조회
                        content_id = gen.get('id', '')
                        adopted_tones = get_content_adopted_tones(content_id) if content_id else []
                        
                        # 불러오기 버튼과 복사한 톤 정보 표시
                        if adopted_tones:
                            # 모든 톤 목록 (6개 톤)
                            all_tones = ['정보전달형', '후기형', '긴급/마감 임박형', '스토리텔링형', '친근한 톤', '유머러스한 형']
                            
                            # 각 톤별로 O/X 표시
                            tone_indicators = []
                            for tone in all_tones:
                                if tone in adopted_tones:
                                    tone_indicators.append(f'<span style="color: #28a745; font-weight: bold;">{tone} ✓</span>')
                                else:
                                    tone_indicators.append(f'<span style="color: #6c757d;">{tone} ✗</span>')
                            
                            # 2열로 배치
                            tone_display = '<br>'.join([
                                '&nbsp;&nbsp;&nbsp;&nbsp;'.join(tone_indicators[:3]),  # 첫 3개
                                '&nbsp;&nbsp;&nbsp;&nbsp;'.join(tone_indicators[3:])   # 나머지 3개
                            ])
                            
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
                                border: 2px solid #28a745;
                                border-radius: 12px;
                                padding: 16px;
                                margin: 8px 0;
                                box-shadow: 0 2px 8px rgba(40, 167, 69, 0.15);
                            ">
                                <div style="
                                    color: #155724;
                                    font-weight: 600;
                                    font-size: 14px;
                                    margin-bottom: 8px;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                ">
                                    <span style="font-size: 18px;">✅</span>
                                    <span>복사한 톤</span>
                                </div>
                                <div style="
                                    color: #155724;
                                    font-size: 13px;
                                    line-height: 1.6;
                                ">
                                    {tone_display}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if st.button(f"📋 불러오기", key=f"load_gen_{start_idx + i}", use_container_width=True):
                            # 히스토리에서 불러오기 로그 기록
                            community = gen.get('community') or gen.get('attributes', {}).get('community', 'unknown')
                            logger.info(f"LOAD_FROM_HISTORY - user_id: {st.session_state.user_id}, content_id: {content_id}, community: {community}")
                            
                            # 해당 생성 결과를 메인 화면에 표시
                            st.session_state.generated_contents = gen.get('generated_contents', [])
                            st.session_state.current_generate_id = content_id  # generate_id 설정
                            st.session_state.selected_community = community  # 커뮤니티 정보 저장
                            st.session_state.show_results = True
                            st.session_state.current_page = "main"  # 메인 페이지로 이동
                            st.rerun()
                    
                    # 생성된 원고 6개 모두 표시
                    if gen.get('generated_contents'):
                        st.markdown("### 📝 생성된 원고")
                        for j, content in enumerate(gen['generated_contents']):
                            tone = content.get('tone', f'톤 {j+1}')
                            text = content.get('text', '')
                            
                            # 복사한 톤인지 확인
                            is_adopted = tone in adopted_tones
                            
                            # 톤별 색상 매핑
                            tone_colors = {
                                '정보전달형': '#e3f2fd',
                                '후기형': '#f3e5f5', 
                                '유머러스한 형': '#fff3e0',
                                '친근한 톤': '#e8f5e8',
                                '긴급/마감 임박형': '#ffebee',
                                '스토리텔링형': '#f1f8e9'
                            }
                            
                            bg_color = tone_colors.get(tone, '#f8f9fa')
                            
                            # 복사한 톤이면 테두리 색상과 아이콘 추가
                            border_color = '#28a745' if is_adopted else '#667eea'
                            adopted_icon = ' ✅' if is_adopted else ''
                            
                            st.markdown(f"""
                            <div style="background-color: {bg_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {border_color}; {'box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);' if is_adopted else ''}">
                                <div style="font-weight: bold; color: #495057; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                    {tone}{adopted_icon}
                                </div>
                                <div style="color: #212529; line-height: 1.6;">
                                    {text}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # 페이지네이션 컨트롤
            if total_pages > 1:
                st.markdown("---")
                
                # 페이지네이션을 중앙 정렬된 컨테이너로 표시
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; padding: 1rem 0;">
                    <span style="padding: 0.5rem 1rem; font-weight: bold; color: #495057; background: #f8f9fa; border-radius: 6px; border: 1px solid #dee2e6;">
                        페이지 {st.session_state.history_page + 1} / {total_pages}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # 버튼들을 중앙 정렬
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                
                with col1:
                    if st.button("⏮️ 처음", key="first_page", help="첫 페이지로 이동", use_container_width=True):
                        st.session_state.history_page = 0
                        st.rerun()
                
                with col2:
                    if st.button("◀️ 이전", key="prev_page", help="이전 페이지로 이동", use_container_width=True):
                        if st.session_state.history_page > 0:
                            st.session_state.history_page -= 1
                            st.rerun()
                
                with col3:
                    st.empty()  # 빈 공간
                
                with col4:
                    if st.button("다음 ▶️", key="next_page", help="다음 페이지로 이동", use_container_width=True):
                        if st.session_state.history_page < total_pages - 1:
                            st.session_state.history_page += 1
                            st.rerun()
                
                with col5:
                    if st.button("끝 ⏭️", key="last_page", help="마지막 페이지로 이동", use_container_width=True):
                        st.session_state.history_page = total_pages - 1
                        st.rerun()
        else:
            st.info("아직 생성 기록이 없습니다. 첫 번째 원고를 생성해보세요! 🚀")
            
    except Exception as e:
        st.error("히스토리를 불러오는 중 오류가 발생했습니다.")
        st.write(f"오류: {str(e)}")
