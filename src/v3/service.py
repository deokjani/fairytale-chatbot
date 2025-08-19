from src.v3.utils import create_unique_session_id
from src.v3.utils import get_character_description
from src.v3.llm_chain import talking_chain, quiz_chain, talking_final_chain
from src.v3.tts import synthesize_text
from src.v3.bad_words_filter import bad_words_filter
from src.v3.bert_cefr import analyze_user_level
import asyncio


async def talking(book_id, character, session_id, query, final, initial=False):
    if not session_id:
        session_id = await create_unique_session_id(length=8)
    
    # yield f"<session_id>={session_id}\n"
    if initial:
        try:
            full_response = ""
            async for response in talking_chain(book_id, initial=True).astream(
                {
                    "question": "[INITIAL_GREETING]",
                    "character": character,
                    "description": get_character_description(book_id, character),
                },
                config={"configurable": {"session_id": session_id}},
            ):
                full_response += response
                yield f"content={response}<session_id>={session_id}\n"
            
            if full_response:
                ai_cefr_level, _ = analyze_user_level(full_response)
                yield f"content=<session_id>={session_id}<AI_CEFR>={ai_cefr_level}\n"
            return
        except Exception as e:
            print(f"Error in initial greeting - session: {session_id}, error: {str(e)}")
            raise
    
    if final:
        try:
            full_response = ""
            async for response in talking_final_chain().astream(
                {"question": query},
                config={"configurable": {"session_id": session_id}},
            ):
                full_response += response
                yield f"content={response}<session_id>={session_id}\n"
            
            return
        except asyncio.CancelledError:
            raise

    # 사용자 query에 대한 CEFR 평가를 먼저 수행
    if query and query.strip():
        user_cefr_level, _ = analyze_user_level(query)
        yield f"content=<USER_CEFR>={user_cefr_level}\n"
    
    # 불용어 체크
    has_bad_words, filter_response = bad_words_filter.filter_text(query)
    if has_bad_words:
        print(f"[TALKING] Bad words filtered - session: {session_id}")
        yield f"content={filter_response}<session_id>={session_id}<AI_CEFR>=A1\n"
        return
    
    # 불용어가 없으면 바로 대화 처리
    try:
        full_response = ""
        async for response in talking_chain(book_id).astream(
                {
                    "question": query,
                    "character": character,
                    "description": get_character_description(book_id, character),
                },
                config={"configurable": {"session_id": session_id}},
        ):
            full_response += response
            yield f"content={response}<session_id>={session_id}\n"

        if full_response:
            ai_cefr_level, _ = analyze_user_level(full_response)
            yield f"content=<session_id>={session_id}<AI_CEFR>={ai_cefr_level}\n"
        
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"Error in talking - session: {session_id}, error: {str(e)}")
        raise


async def quiz(book_id, session_id, query, final):
    if not session_id:
        session_id = await create_unique_session_id(length=8)
    try:
        async for response in quiz_chain(book_id, final).astream(
                {"query": query},
                # 세션 ID 기준으로 대화를 기록합니다.
                config={"configurable": {"session_id": session_id}},
                ):
            yield f"content={response}<session_id>={session_id}\n"

    except asyncio.CancelledError:
        print("Client disconnected")
        raise


async def tts(text, speaker, speed):
    return await synthesize_text(text, speaker, speed)