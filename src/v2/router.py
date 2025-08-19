from fastapi import APIRouter, Form, Request
from fastapi.params import Param
from fastapi.responses import StreamingResponse
from src.v2.service import talking, quiz, tts
from src.v2.utils import ebook_lists, get_characters


router_v1 = APIRouter(
    prefix="/v1/book",
    tags=["Book Talking"],
)

@router_v1.get(
    "/list"
)
async def _list():
    return ebook_lists

@router_v1.get(
    "/character"
)
async def _character(
    book_id: str = Param(
        default=...,
        title="Book ID",
        description="Book id를 입력해 주세요. 예) ACS001"
    ),
):
    return get_characters(book_id)
    # return Response(content=get_character(book_id), status_code=status.HTTP_200_OK)

@router_v1.post(
    "/talking"
)
async def _talking(
    request: Request,
    book_id: str = Form(
        default=...,
        title="Book ID",
        description="Book id를 입력해 주세요. 예) ACS001"
    ),
    character: str = Form(
        default="main",
        title="Character Name",
        description="캐릭터 이름 입니다. 예) Famer"
    ),
    session_id: str = Form(
        default="",
        title="대화 session_id",
        description="대화 이력이 session_id 별로 기록 됩니다. 첫 대화의 경우 빈 값으로 두세요."
    ),
    query: str = Form(
        default="",
        title="사용자 입력 값",
        description="사용자의 입력 값 입니다. 예) How big are turnips?"
    ),
    final: bool = Form(
        default=False,
        title="대화 종료",
        description="대화 종료 시 True. 대화 종료 후 CEFR 을 리턴합니다."
    ),
):
    return StreamingResponse(talking(book_id, character, session_id, query, final), media_type="text/event-stream")

@router_v1.post(
    "/quiz"
)
async def _quiz(
    request: Request,
    book_id: str = Form(
        default="ACS001",
        title="Book ID",
        description="Book id를 입력해 주세요. 예) ACS001"
    ),
    session_id: str = Form(
        default="",
        title="대화 session_id",
        description="대화 이력이 session_id 별로 기록 됩니다. 첫 대화의 경우 빈 값으로 두세요."
    ),
    query: str = Form(
        default="",
        title="사용자 입력 값",
        description="사용자의 입력 값 입니다."
    ),
    final: bool = Form(
        default=False,
        title="대화 종료",
        description="대화 종료 시 True. 대화 종료 후 AI가 평가합니다."
    ),
):
    return StreamingResponse(quiz(book_id, session_id, query, final), media_type="text/event-stream")


@router_v1.post(
    "/tts"
)
async def _tts(
    request: Request,
    text: str = Form(default="This is test", title="Text", description="TTS Text"),
    speaker: str = Form(
        default="en-US-Chirp3-HD-Achernar",
        title="TTS Speaker",
        description="TTS 목소리",
    ),
    speed: float = Form(
        default="0.9", title="TTS Speed", description="TTS 속도. 0.25 <= speed <= 4.0"
    ),
):
    return StreamingResponse(await tts(text, speaker, speed), media_type="audio/mp3")
