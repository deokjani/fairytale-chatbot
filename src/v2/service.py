from src.v2.utils import create_unique_session_id
from src.v2.utils import get_character_description
from src.v2.llm_chain import talking_chain, quiz_chain, talking_final_chain
from src.v2.tts import synthesize_text
import asyncio


async def talking(book_id, character, session_id, query, final):
    if not session_id:
        session_id = await create_unique_session_id(length=8)
    # yield f"<session_id>={session_id}\n"
    if final:
        try:
            async for response in talking_final_chain().astream(
                    {"question": query,
                     },
                    # 세션 ID 기준으로 대화를 기록합니다.
                    config={"configurable": {"session_id": session_id}},
            ):
                yield f"content={response}<session_id>={session_id}\n"
            return
        except asyncio.CancelledError:
            print("Client disconnected")
            raise
    try:
        async for response in talking_chain(book_id).astream(
                {"question": query,
                 "character": character,
                 "description": get_character_description(book_id, character),
                 },
                # 세션 ID 기준으로 대화를 기록합니다.
                config={"configurable": {"session_id": session_id}},
                ):
            yield f"content={response}<session_id>={session_id}\n"
    except asyncio.CancelledError:
        print("Client disconnected")
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