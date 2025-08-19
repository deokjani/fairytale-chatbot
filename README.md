# AI 동화책 챗봇 - 적응형 영어 학습 시스템

**초1~고1학생을 위한 AI 기반 영어 난이도 자동 조절 및 평가 시스템**

<div align="center">
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
  [![CEFR](https://img.shields.io/badge/CEFR-A1--C2-green)](https://www.coe.int/)
  [![BERT](https://img.shields.io/badge/Model-BERT--based-orange)](https://huggingface.co/)
  [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
  
</div>

<br>

<div align="center">
  <kbd>
    <img width="800" alt="CEFR 기반 실시간 레벨 평가 화면" src="https://github.com/user-attachments/assets/f4ed0408-ed37-4dad-9674-ee0f798b16b7" />
  </kbd>
  <br><br>
  <b>✨ CEFR 기반 실시간 레벨 평가 화면 데모 ✨</b>
</div>

<br>

## 📌 프로젝트 소개

학습자의 영어 실력에 따라 **대화 난이도를 실시간으로 조절**하는 AI 챗봇입니다. 학생을 대상으로 동화책 기반의 흥미로운 대화를 생성하며, **CEFR 기준**과 **BERT 기반 평가**를 통해 각 학생의 영어 수준을 지속적으로 평가하고 적응합니다.

### ✨ 주요 기능

- 🎯 **실시간 CEFR 레벨 조절** - A1부터 C2까지 자동 난이도 조정
- 💬 **자연스러운 대화 생성** - LLM을 활용한 문맥 인식 대화
- 📊 **BERT 기반 평가** - `AbdulSami/bert-base-cased-cefr` 모델로 정확한 수준 측정
- 🔍 **L2SCA 통합** - 23개 구문 복잡도 지표로 상세 분석
- 🛡️ **안전한 학습 환경** - 부적절한 언어 감지 및 교정

## 🚀 빠른 시작

### 시스템 요구사항

- Python 3.10+
- Java 8+ (L2SCA 실행용)
- CUDA GPU (선택사항)
- Poetry

### 실행

```bash
# Streamlit 앱 실행
poetry run streamlit run src/streamlit_app.py --server.port 7135

# 웹 브라우저에서 접속
# http://localhost:7135
```

## 📊 기술 스택

### AI/ML 모델
- **대화 생성**: OpenAI GPT
- **레벨 평가**: BERT (`AbdulSami/bert-base-cased-cefr`)

### 백엔드
- **웹 프레임워크**: FastAPI, Streamlit
- **세션 관리**: Redis
- **구문 분석**: L2SCA (Java 기반)

## 🎯 CEFR 레벨 시스템

| 레벨 | 수준 | 특징 | 예시 문장 |
|------|------|------|-----------|
| **A1** | 입문 | 기초 단어와 간단한 문장 | "I like apple" |
| **A2** | 초급 | 일상 표현과 기본 시제 | "I went to school yesterday" |
| **B1** | 중급 | 복문과 조건문 사용 | "If I have time, I will visit you" |
| **B2** | 중상급 | 관계절과 종속절 활용 | "The book that I read was interesting" |
| **C1** | 상급 | 복잡한 구문과 추상 개념 | "Despite the circumstances, we achieved our goals" |
| **C2** | 최상급 | 원어민 수준의 표현 | "The ramifications will reverberate throughout" |

## 📈 성능 지표

### CEFR-SP 데이터셋 평가 결과

- **전체 정확도**: 43.2%
- **인접 레벨 정확도**: 90.6%
- **Macro F1 Score**: 0.226

> 💡 인접 레벨 간 높은 구분 정확도로 점진적 난이도 조절에 최적화

## 🔧 핵심 구현

### 1. 적응형 난이도 조절

```python
def adjust_difficulty(user_input):
    # 1. BERT 모델로 CEFR 레벨 평가
    current_level = evaluate_cefr(user_input)
    
    # 2. 신뢰도 기반 레벨 안정화
    stabilized_level = stabilize_level(current_level, history)
    
    # 3. LLM에 적절한 난이도로 응답 생성 요청
    response = generate_response(stabilized_level)
    
    return response
```

### 2. 극단 레벨 처리

- **A1 (초급)**: 7단어 미만 자동 판정, 단순 어휘 사용
- **C2 (고급)**: 명시적 고급 표현 요청, 복잡한 구문 생성

## 💡 개발 인사이트

### 프롬프트 엔지니어링
✅ **효과적인 방법**
- 명확하고 간결한 지시사항
- 중요 내용은 프롬프트 앞뒤 배치
- CEFR 기준 명시 (LLM이 친숙한 표준)

❌ **피해야 할 방법**
- 복잡한 다중 조건
- L2SCA 같은 생소한 지표 직접 사용
- Chain of Thought (오버엔지니어링)

### 모델 조합 전략
- **BERT**: 안정적이고 일관된 평가
- **LLM**: 창의적이고 자연스러운 대화
- **하이브리드**: 두 모델의 장점 결합


## 📚 참고 자료

- [CEFR Framework](https://www.coe.int/en/web/common-european-framework-reference-languages)
- [BERT CEFR Model](https://huggingface.co/AbdulSami/bert-base-cased-cefr)
- [L2SCA Tool](https://sites.psu.edu/xxl13/l2sca/)
- [CEFR-SP Dataset](https://doi.org/10.18653/v1/2022.emnlp-main.416)
