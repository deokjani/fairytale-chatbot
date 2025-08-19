# 슈필라움 AI 동화책 챗봇

## 📚 프로젝트 개요

슈필라움(Spielraum)은 초등학생을 위한 AI 기반 영어 동화책 대화 시스템입니다. CEFR 레벨 기반으로 학습자 수준에 맞춰 자동으로 난이도를 조절하며, 실시간으로 대화를 평가합니다.

### 주요 특징
- 🎯 **CEFR 기반 난이도 자동 조절** (A1~C2)
- 💬 **자연스러운 대화 생성** (LLM 활용)
- 📊 **실시간 영어 수준 평가** (BERT 모델)
- 🔍 **구문 복잡도 분석** (L2SCA 통합)

## 🛠️ 기술 스택

- **Backend**: FastAPI, Streamlit
- **AI/ML**: 
  - OpenAI GPT (대화 생성)
  - BERT (CEFR 레벨 평가)
  - AbdulSami/bert-base-cased-cefr 모델
- **Database**: Redis (세션 관리)
- **Languages**: Python 3.10+

## 🚀 설치 및 실행

### 1. 환경 요구사항
```bash
# Python 3.10 이상
# Poetry (패키지 관리)
# Java 8+ (L2SCA 실행용)
```

### 2. 프로젝트 설정
```bash
# 클론
git clone [repository-url]
cd ai-book_spielraum

# 환경 변수 설정
cp .env_sample .env
# .env 파일에 OpenAI API 키 등 설정

# 의존성 설치
poetry install
```

### 3. 실행
```bash
# Streamlit 앱 실행
poetry run streamlit run src/streamlit_app.py --server.port 7135
```

## 📁 프로젝트 구조

```
ai-book_spielraum/
├── src/
│   ├── streamlit_app.py   # Streamlit UI
│   ├── api.py             # FastAPI 서버
│   ├── v1/                # API v1 (기본 구현)
│   ├── v2/                # API v2 (개선 버전)
│   └── v3/                # API v3 (최신 버전)
├── pyproject.toml         # Poetry 의존성
└── poetry.lock           # 의존성 잠금
```

## 🧠 핵심 기능

### 1. CEFR 레벨 평가
- **모델**: `AbdulSami/bert-base-cased-cefr`
- **레벨**: A1(초급) ~ C2(원어민)
- **특징**: 실시간 문장 난이도 평가

### 2. 적응형 대화 생성
```python
# 사용자 레벨에 맞춘 응답 생성
def generate_response(user_level: str, context: str):
    # CEFR 레벨 기반 프롬프트 조정
    # 어휘, 문법 복잡도 자동 조절
    return ai_response
```

### 3. 난이도 조절 메커니즘
- 사용자 입력 분석 → CEFR 레벨 판정
- 신뢰도 기반 레벨 안정화
- 점진적 난이도 조정

## 📊 성능 평가

- **정확도**: 43.2% (CEFR-SP 데이터셋)
- **Adjacent Accuracy**: 90.6%
- **특징**: 인접 레벨 간 높은 구분 정확도

## 💡 개발 인사이트

### 프롬프트 엔지니어링
- 명확하고 간결한 지시사항이 핵심
- CEFR이 L2SCA보다 LLM에게 친숙
- 중요 내용은 프롬프트 앞뒤 배치

### 모델 조합 전략
- **BERT**: 안정적이고 일관된 평가
- **LLM**: 창의적이고 자연스러운 대화
- **하이브리드**: 두 모델의 장점 결합

## 🔜 향후 개선 계획

1. **평가 정확도 향상**
   - Oxford 5000 단어 리스트 파인튜닝
   - 문장 수준 데이터 추가 학습

2. **하이브리드 평가**
   - BERT + LLM 가중치 조합
   - 신뢰도 기반 동적 조정

3. **사용자 경험 개선**
   - 실시간 피드백 강화
   - 학습 진도 시각화

## 📚 참고 자료

- [CEFR Framework](https://www.coe.int/en/web/common-european-framework-reference-languages)
- [Hugging Face Model](https://huggingface.co/AbdulSami/bert-base-cased-cefr)
- [L2SCA](https://sites.psu.edu/xxl13/l2sca/)

## 📝 라이선스

교육 및 연구 목적으로 개발되었습니다.

---

**Note**: 이 프로젝트는 지속적으로 개발 중입니다. 상세한 설정이나 데이터는 별도 문의 바랍니다.