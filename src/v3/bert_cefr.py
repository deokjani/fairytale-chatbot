"""
BERT CEFR Prediction - 통합 버전
레벨 예측, 안정화 기능 및 난이도 설정 관리
"""
from transformers import pipeline
from typing import Dict, List, Tuple, Optional, Any

# 난이도별 설정 - 6단계로 세분화
DIFFICULTY_CONFIGS = {
    "A1": {
        "mlt_range": (0, 3.0),
        "talking": {
            "word_limit": 5,
            "sentence_count": "1",
            "vocab_level": "very basic"
        },
        "quiz": {
            "question_words": "3-5",
            "choice_words": "1-2",
            "vocab_level": "very basic vocabulary"
        }
    },
    "A2": {
        "mlt_range": (3.0, 6.0),
        "talking": {
            "word_limit": 10,
            "sentence_count": "1-2",
            "vocab_level": "basic"
        },
        "quiz": {
            "question_words": "5-8",
            "choice_words": "2-3",
            "vocab_level": "basic vocabulary"
        }
    },
    "B1": {
        "mlt_range": (6.0, 9.0),
        "talking": {
            "word_limit": 15,
            "sentence_count": "2",
            "vocab_level": "common"
        },
        "quiz": {
            "question_words": "8-12",
            "choice_words": "3-5",
            "vocab_level": "common vocabulary"
        }
    },
    "B2": {
        "mlt_range": (9.0, 12.0),
        "talking": {
            "word_limit": 20,
            "sentence_count": "2-3",
            "vocab_level": "varied"
        },
        "quiz": {
            "question_words": "12-15",
            "choice_words": "5-7",
            "vocab_level": "varied vocabulary"
        }
    },
    "C1": {
        "mlt_range": (12.0, 15.0),
        "talking": {
            "word_limit": 25,
            "sentence_count": "3",
            "vocab_level": "advanced"
        },
        "quiz": {
            "question_words": "15-18",
            "choice_words": "7-9",
            "vocab_level": "advanced vocabulary"
        }
    },
    "C2": {
        "mlt_range": (15.0, float('inf')),
        "talking": {
            "word_limit": 30,
            "sentence_count": "3-4",
            "vocab_level": "sophisticated"
        },
        "quiz": {
            "question_words": "18-20",
            "choice_words": "9-10",
            "vocab_level": "sophisticated vocabulary"
        }
    }
}


class BertCEFRPredictor:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification", 
            model="AbdulSami/bert-base-cased-cefr"
        )
        
        # 레벨 매핑
        self.level_map = {
            'A1': 1, 'A2': 2, 'B1': 3, 
            'B2': 4, 'C1': 5, 'C2': 6
        }
        
        self.reverse_map = {
            1: 'A1', 2: 'A2', 3: 'B1',
            4: 'B2', 5: 'C1', 6: 'C2'
        }
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        CEFR 레벨 예측
        Returns: {
            'level': 예측 레벨,
            'confidence': 신뢰도,
            'needs_llm': LLM 필요 여부,
            'all_scores': 모든 레벨 점수
        }
        """
        # 디버깅: 모든 텍스트에 대해 단어 수 출력
        word_count = len(text.split())
        print(f"[DEBUG] Analyzing text: '{text}' - Word count: {word_count}")
        
        # 7단어 미만은 A1
        if word_count < 7:
            print(f"[DEBUG] -> Returning A1 due to word count < 7")
            return {
                'level': 'A1',
                'confidence': 'low',
                'needs_llm': False,
                'reason': f'Too short ({word_count} words)',
                'all_scores': [  # 가짜 scores 추가
                    {'label': 'A1', 'score': 0.95},
                    {'label': 'A2', 'score': 0.05}
                ]
            }
        
        # BERT 예측
        results = self.classifier(text, top_k=6)
        first = results[0]
        second = results[1]
        gap = first['score'] - second['score']
        
        # 결과 분석
        if gap < 0.15:  # 애매한 경우
            return {
                'level': first['label'],
                'confidence': 'low',
                'needs_llm': True,
                'candidates': [first['label'], second['label']],
                'all_scores': results
            }
        else:  # 확실한 경우
            return {
                'level': first['label'],
                'confidence': 'high' if gap > 0.3 else 'medium',
                'needs_llm': False,
                'score': first['score'],
                'all_scores': results
            }
    
    def get_difficulty_from_cefr(self, level: str) -> str:
        """CEFR 레벨을 난이도로 변환"""
        mapping = {
            'A1': 'SIMPLE',
            'A2': 'SIMPLE',
            'B1': 'MODERATE',
            'B2': 'MODERATE',
            'C1': 'ADVANCED',
            'C2': 'ADVANCED'
        }
        return mapping.get(level, 'MODERATE')


# 전역 인스턴스 (한 번만 로드)
bert_predictor = BertCEFRPredictor()


def analyze_user_level(text: str) -> Tuple[str, bool]:
    """
    사용자 텍스트의 CEFR 레벨 분석
    Returns: (레벨, LLM 필요 여부)
    """
    result = bert_predictor.predict(text)
    return result['level'], result['needs_llm']


def evaluate_text_cefr(text: str) -> Tuple[str, str, Dict]:
    """
    텍스트의 CEFR 레벨과 신뢰도 평가
    Returns: (CEFR 레벨, 신뢰도, 전체 결과)
    """
    result = bert_predictor.predict(text)
    return result['level'], result['confidence'], result


def evaluate_last_message_cefr(chat_history: List) -> str:
    """
    채팅 히스토리에서 마지막 사용자 메시지의 CEFR 레벨 평가
    Returns: CEFR 레벨 문자열
    """
    if not chat_history:
        return "A1"
    
    # 마지막 사용자 메시지 찾기
    for message in reversed(chat_history):
        if hasattr(message, 'type') and message.type == 'human':
            result = bert_predictor.predict(message.content)
            return result['level']
        elif isinstance(message, dict) and message.get('role') == 'user':
            result = bert_predictor.predict(message['content'])
            return result['level']
    
    return "A1"  # 기본값


def stabilize_ai_response_level(user_level: str, ai_predicted_level: str) -> str:
    """
    AI 응답 레벨을 유저 레벨에 맞춰 안정화
    
    Args:
        user_level: 유저의 현재 CEFR 레벨
        ai_predicted_level: AI가 예측한 CEFR 레벨
        
    Returns:
        안정화된 CEFR 레벨
    """
    # 레벨 매핑 사용
    level_map = bert_predictor.level_map
    reverse_map = bert_predictor.reverse_map
    
    user_num = level_map.get(user_level, 1)
    ai_num = level_map.get(ai_predicted_level, 1)
    
    # ±1 레벨 범위로 제한
    min_allowed = max(1, user_num - 1)
    max_allowed = min(6, user_num + 1)
    
    if ai_num < min_allowed:
        return reverse_map[min_allowed]
    elif ai_num > max_allowed:
        return reverse_map[max_allowed]
    else:
        return ai_predicted_level


def process_bert_cefr_for_talking(user_text: str, ai_predicted_level: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    BERT CEFR를 사용하여 대화용 난이도와 설정을 반환합니다.
    
    Args:
        user_text: 사용자 입력 텍스트
        ai_predicted_level: AI가 예측한 레벨 (선택사항)
        
    Returns:
        (난이도, 설정 딕셔너리)
    """
    # BERT로 사용자 레벨 분석
    user_level, needs_llm = analyze_user_level(user_text)
    
    # AI 응답 레벨 안정화 (필요한 경우)
    if ai_predicted_level:
        target_level = stabilize_ai_response_level(user_level, ai_predicted_level)
    else:
        target_level = user_level
    
    # 해당 레벨의 설정 반환
    config = DIFFICULTY_CONFIGS[target_level]["talking"]
    
    return target_level, config


def process_bert_cefr_for_quiz(user_text: str) -> Tuple[str, Dict[str, str]]:
    """
    BERT CEFR를 사용하여 퀴즈용 난이도와 설정을 반환합니다.
    
    Args:
        user_text: 사용자 입력 텍스트
        
    Returns:
        (난이도, 설정 딕셔너리)
    """
    # BERT로 사용자 레벨 분석
    user_level, _ = analyze_user_level(user_text)
    
    # 해당 레벨의 퀴즈 설정 반환
    return user_level, DIFFICULTY_CONFIGS[user_level]["quiz"]


def get_difficulty_config(level: str, mode: str = "talking") -> Dict[str, Any]:
    """
    특정 레벨과 모드에 대한 설정을 반환합니다.
    
    Args:
        level: CEFR 레벨 (A1~C2)
        mode: "talking" 또는 "quiz"
        
    Returns:
        설정 딕셔너리
    """
    if level not in DIFFICULTY_CONFIGS:
        level = "A1"  # 기본값
    
    return DIFFICULTY_CONFIGS[level].get(mode, DIFFICULTY_CONFIGS[level]["talking"])