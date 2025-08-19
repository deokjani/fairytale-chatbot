from src.v2.params import REDIS_URL, OPENAI_API_KEY
from src.v2.prompt import quiz_prompt, talking_prompt, quiz_final_prompt, talking_final_prompt
from src.v2.retriever import load_retriever, load_full_context
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from operator import itemgetter

llm = ChatOpenAI(
    model="gpt-4.1",
    api_key=OPENAI_API_KEY,
    stream_usage=True,
)

# Redis
def get_message_history(session_id: str) -> RedisChatMessageHistory:
    # 세션 ID를 기반으로 RedisChatMessageHistory 객체를 반환합니다.
    return RedisChatMessageHistory(session_id, url=REDIS_URL, ttl=3600)


def talking_chain(book_id):
    # RAG Chain
    chain = (
            {
                "character": itemgetter("character"),
                "description": itemgetter("description"),
                "context": itemgetter("question") | load_retriever(book_id),
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | talking_prompt
            | llm
            | StrOutputParser()
    )
    rag_with_history = RunnableWithMessageHistory(
        chain,
        get_message_history,  # 세션 기록을 가져오는 함수
        input_messages_key="question",  # 사용자의 질문이 템플릿 변수에 들어갈 key
        history_messages_key="chat_history",  # 기록 메시지의 키
    )
    return rag_with_history

def talking_final_chain():
    # RAG Chain
    chain = (
            {
                "chat_history": itemgetter("chat_history"),
            }
            | talking_final_prompt
            | llm
            | StrOutputParser()
    )
    rag_with_history = RunnableWithMessageHistory(
        chain,
        get_message_history,  # 세션 기록을 가져오는 함수
        input_messages_key="question",  # 사용자의 질문이 템플릿 변수에 들어갈 key
        history_messages_key="chat_history",  # 기록 메시지의 키
    )
    return rag_with_history

def quiz_chain(book_id, final):
    # RAG Chain
    chain = (
        {
            # "context": itemgetter("query") | load_full_context(book_id),
            "context": itemgetter("query") | load_retriever(book_id),
            "query": itemgetter("query"),
            "chat_history": itemgetter("chat_history"),
        }
        | quiz_prompt
        | llm
        | StrOutputParser()
    )
    if final:
        chain = (
                {
                    "chat_history": itemgetter("chat_history"),
                }
                | quiz_final_prompt
                | llm
                | StrOutputParser()
        )
    rag_with_history = RunnableWithMessageHistory(
        chain,
        get_message_history,  # 세션 기록을 가져오는 함수
        input_messages_key="query",  # 사용자의 질문이 템플릿 변수에 들어갈 key
        history_messages_key="chat_history",  # 기록 메시지의 키
    )
    return rag_with_history
