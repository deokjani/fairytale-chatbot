"""
불용어 필터링 모듈
bad_words.txt 파일을 읽어서 부적절한 단어를 검사합니다.
"""
import os
import re
from typing import Tuple, Set, Optional

class BadWordsFilter:
    def __init__(self, bad_words_file: str = None):
        """
        불용어 필터 초기화
        
        Args:
            bad_words_file: 불용어 파일 경로
        """
        if bad_words_file is None:
            # 기본 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bad_words_file = os.path.join(current_dir, 'bad_words.txt')
        
        self.bad_words = self._load_bad_words(bad_words_file)
        self.inappropriate_response = "Let’s keep our chat nice and safe for everyone!"
    
    def _load_bad_words(self, file_path: str) -> Set[str]:
        """불용어 파일 로드"""
        bad_words = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        bad_words.add(word)
        except FileNotFoundError:
            print(f"Warning: Bad words file not found at {file_path}")
        except Exception as e:
            print(f"Error loading bad words file: {e}")
        
        return bad_words
    
    def contains_bad_words(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        텍스트에 불용어가 포함되어 있는지 검사
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            (불용어 포함 여부, 발견된 첫 번째 불용어)
        """
        if not text:
            return False, None
        
        # 텍스트를 소문자로 변환하고 단어로 분리
        text_lower = text.lower()
        # 단어 경계를 사용한 정규식으로 단어 추출
        words = re.findall(r'\b\w+\b', text_lower)
        
        # 각 단어가 불용어인지 검사 (정확히 일치하는 경우만)
        for word in words:
            if word in self.bad_words:
                return True, word
        
        return False, None
    
    def filter_text(self, text: str) -> Tuple[bool, str]:
        """
        텍스트를 필터링하고 적절한 응답 반환
        
        Args:
            text: 필터링할 텍스트
            
        Returns:
            (불용어 포함 여부, 응답 메시지)
        """
        # None이거나 빈 문자열 처리
        if not text:
            return False, ""
        
        # 문자열이 아닌 경우 문자열로 변환
        text = str(text).strip()
        
        # 빈 문자열인 경우
        if not text:
            return False, ""
        
        has_bad_words, bad_word = self.contains_bad_words(text)
        
        if has_bad_words:
            print(f"[BAD WORDS DETECTED] Word: '{bad_word}' found in text: '{text}'")
            return True, self.inappropriate_response
        
        return False, text

# 전역 인스턴스 생성
bad_words_filter = BadWordsFilter()