# 커뮤니티 바이럴 콘텐츠 생성 시스템

AI 기반 커뮤니티별 맞춤형 바이럴 콘텐츠 자동 생성 플랫폼

## 설치 및 실행

### 1. Poetry 설치
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 프로젝트 클론 및 의존성 설치
```bash
git clone <repository-url>
cd community-persona-ai
poetry install --no-root
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 Gemini API 키를 설정하세요:
```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

### 4. 앱 실행
```bash
poetry run streamlit run main.py
```

## 프로젝트 구조

```
community-persona-ai/
├── main.py                 # 메인 애플리케이션 진입점
├── frontend/               # UI 컴포넌트 및 페이지
│   ├── components/         # 재사용 가능한 UI 컴포넌트
│   │   └── ui_helpers.py   # UI 헬퍼 함수들
│   └── pages/              # 각 화면별 페이지
│       ├── login.py        # 로그인 페이지
│       ├── user_input.py   # 입력 폼 페이지
│       └── copy_result.py  # 결과 표시 페이지
├── services/               # 비즈니스 로직
│   ├── user_service.py     # 사용자 관리
│   ├── content_service.py  # 콘텐츠 생성 및 관리(비즈니스 로직)
│   └── ai_service.py       # AI API 통합
├── database/               # 데이터베이스 관련
│   ├── connection.py       # DB 연결 관리
│   └── crud.py             # CRUD 작업
├── prompts/                # 프롬프트 템플릿
│   ├── mam2bebe.yaml       # 맘이베베 프롬프트
│   ├── ppomppu.yaml        # 뽐뿌 프롬프트
│   ├── fmkorea.yaml        # 에펨코리아 프롬프트
│   └── regenerate_*.yaml   # 재생성 프롬프트(맘이베베 / 뽐뿌 / 에펨코리아)
├── utils/                  # 유틸리티 함수
│   ├── validators.py       # 입력 검증
│   └── get_logger.py       # 로깅 설정
├── data/                   # 데이터 저장소
│   └── database/           # SQLite 데이터베이스
├── logs/                   # 로그 파일(info / error)
└── .env                    # 환경 변수 설정
```
