import streamlit as st
import asyncio
import sys
import os
import json


# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.v3.utils import create_unique_session_id, get_character_description, get_characters
from src.v3.llm_chain import talking_chain, talking_final_chain
from src.v3.bert_cefr import evaluate_text_cefr, stabilize_ai_response_level

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def get_book_name(book_id):
    """책 ID로부터 책 제목을 가져오는 함수"""
    try:
        with open(f'ebook/{book_id}/common/data/ebook_data.json', 'r', encoding='utf-8') as file:
            ebook_data = json.load(file)
            return ebook_data.get("BOOK_NAME", book_id)
    except:
        return book_id

def get_book_summary(book_id):
    """책의 내용을 요약하는 함수"""
    try:
        with open(f'ebook/{book_id}/common/data/ebook_data.json', 'r', encoding='utf-8') as file:
            ebook_data = json.load(file)
            pages = ebook_data.get("PAGE", [])
            
            # 모든 페이지의 텍스트를 수집
            full_text = ""
            for page in pages:
                page_text = page.get("PAGE_TEXT", "").strip()
                if page_text:
                    full_text += page_text + " "
            
            # 텍스트가 너무 길면 처음 500자만 사용
            if len(full_text) > 500:
                return full_text[:500] + "..."
            return full_text if full_text else "No summary available."
    except:
        return "Summary not available."

# AI가 먼저 대화를 시작하는 함수
async def generate_initial_message(book_id, character):
    """책 내용을 기반으로 캐릭터가 먼저 인사하고 질문하는 메시지를 생성"""
    
    full_response = ""
    # initial=True를 사용하여 초기 대화 생성
    async for chunk in talking_chain(book_id, initial=True).astream(
        {
            "question": "[INITIAL_GREETING]",
            "character": character,
            "description": get_character_description(book_id, character)
        },
        config={"configurable": {"session_id": st.session_state.session_id}}
    ):
        full_response += chunk
    
    return full_response

# 5권의 책만 선택
selected_book_ids = ["ACS007", "ECR001", "LSR001", "MFC001", "PFR001"]

# 책 ID와 이름을 매핑하는 딕셔너리 생성
book_name_to_id = {}
for book_id in selected_book_ids:
    book_name = get_book_name(book_id)
    book_name_to_id[book_name] = book_id

st.set_page_config(page_title="Fairy Tale Chatbot", page_icon="📚")

# 세션 상태 초기화
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_book_character' not in st.session_state:
    st.session_state.current_book_character = None

st.title("Fairy Tale Chatbot")

# 사이드바
with st.sidebar:
    selected_book_name = st.selectbox("Book", list(book_name_to_id.keys()))
    book_id = book_name_to_id[selected_book_name]
    
    characters = get_characters(book_id)
    character = st.selectbox("Character", characters) if characters else None
    
    # 책이나 캐릭터가 변경되었는지 확인
    current_selection = (book_id, character)
    if st.session_state.current_book_character != current_selection:
        st.session_state.current_book_character = current_selection
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()
    
    if st.button("Reset"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.current_book_character = None
        st.rerun()
    
    # 책 요약 표시
    st.divider()
    st.subheader("Book Summary")
    book_summary = get_book_summary(book_id)
    st.write(book_summary)
    
    # Book Summary 아래는 비워둠 (CEFR Level Statistics 제거됨)

# 메인 채팅 영역
st.subheader(f"Talking with {character} - {selected_book_name}")

# 세션 초기화 및 첫 메시지 생성 
if not st.session_state.session_id and character:
    st.session_state.session_id = run_async(create_unique_session_id(length=8))
    print(f"[INFO] Created new session: {st.session_state.session_id}")
    
    # 챗봇이 먼저 인사하고 질문하기
    with st.spinner(f"{character} is thinking..."):
        initial_message = run_async(generate_initial_message(book_id, character))
        
        # AI 응답 CEFR 평가
        ai_level, ai_confidence, ai_result = evaluate_text_cefr(initial_message)
        
        # 초기 메시지 저장
        st.session_state.messages.append({
            "role": "assistant", 
            "content": initial_message,
            "cefr_level": ai_level,
            "cefr_confidence": ai_confidence
        })

# 채팅 메시지 표시 (저장된 CEFR 레벨과 함께)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write(msg["content"])
        with col2:
            if "cefr_level" in msg and msg["cefr_level"]:
                st.write(f"**{msg['cefr_level']}**")

# 사용자 입력 처리
if prompt := st.chat_input("Type here..."):
    # 사용자 CEFR 평가 (BERT 사용)
    user_level, user_confidence, user_result = evaluate_text_cefr(prompt)
    print(f"[INFO] User CEFR: {user_level} (confidence: {user_confidence})")
    if 'all_scores' in user_result and len(user_result['all_scores']) >= 2:
        top_scores = user_result['all_scores'][:2]
        print(f"[INFO] User Top 2 scores: {top_scores[0]['label']}={top_scores[0]['score']:.4f}, {top_scores[1]['label']}={top_scores[1]['score']:.4f}")
    
    # 사용자 메시지 추가 (CEFR 레벨 포함)
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "cefr_level": user_level,
        "cefr_confidence": user_confidence
    })
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write(prompt)
        with col2:
            st.write(f"**{user_level}**")
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        col1, col2 = st.columns([10, 1])
        with col1:
            placeholder = st.empty()
        ai_cefr_placeholder = col2.empty()
        
        async def get_response():
            full_response = ""
            description = get_character_description(book_id, character) if character else ""
            
            # L2SCA를 사용한 난이도 조정과 함께 talking_chain 사용
            async for chunk in talking_chain(book_id).astream(
                {
                    "question": prompt,
                    "character": character,
                    "description": description
                },
                config={"configurable": {"session_id": st.session_state.session_id}}
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
                
            placeholder.markdown(full_response)
            return full_response
        
        # AI 응답 생성
        response = run_async(get_response())
        
        # AI 응답 CEFR 평가 (BERT 사용)
        ai_level, ai_confidence, ai_result = evaluate_text_cefr(response)
        
        # 레벨 안정화 적용 (bert_cefr 모듈 사용)
        stabilized_level = stabilize_ai_response_level(user_level, ai_level)
        
        print(f"[INFO] AI CEFR: {ai_level} -> Stabilized: {stabilized_level} (confidence: {ai_confidence})")
        if 'all_scores' in ai_result and len(ai_result['all_scores']) >= 2:
            top_scores = ai_result['all_scores'][:2]
            print(f"[INFO] AI Top 2 scores: {top_scores[0]['label']}={top_scores[0]['score']:.4f}, {top_scores[1]['label']}={top_scores[1]['score']:.4f}")
        
        ai_cefr_placeholder.write(f"**{stabilized_level}**")
        
        # AI 메시지 저장 (CEFR 레벨 포함)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "cefr_level": stabilized_level,  # 안정화된 레벨 사용
            "cefr_confidence": ai_confidence
        })