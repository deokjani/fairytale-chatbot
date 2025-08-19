from src.v3.params import REDIS_URL, OPENAI_API_KEY
from src.v3.prompt import quiz_prompt, talking_prompt, quiz_final_prompt, talking_final_prompt, initial_talking_prompt
from src.v3.retriever import load_retriever, load_full_context
from src.v3.l2sca import get_l2sca_metrics
from src.v3.bert_cefr import evaluate_last_message_cefr, process_bert_cefr_for_quiz, process_bert_cefr_for_talking
from src.v3.bad_words_filter import bad_words_filter
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from operator import itemgetter

from langchain_core.runnables import RunnableLambda

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY,
    stream_usage=True,
)

# Redis
def get_message_history(session_id: str) -> RedisChatMessageHistory:
    # 세션 ID를 기반으로 RedisChatMessageHistory 객체를 반환합니다.
    return RedisChatMessageHistory(session_id, url=REDIS_URL, ttl=3600)


def talking_chain(book_id, initial=False):
    # RAG Chain
    def process_talking_input(x):
        # 초기 대화인 경우
        if initial:
            return {
                "character": x["character"],
                "description": x["description"],
                "context": load_retriever(book_id).invoke("story summary"),  # 간단한 컨텍스트
                "question": "[INITIAL_GREETING]",
                "chat_history": []
            }
        
        # BERT CEFR를 사용한 난이도 분석
        difficulty, config = process_bert_cefr_for_talking(x["question"])
        
        return {
            "character": x["character"],
            "description": x["description"],
            "context": load_retriever(book_id).invoke(x["question"]),
            "question": x["question"],
            "chat_history": x["chat_history"],
            "difficulty": difficulty,
            "word_limit": config["word_limit"],
            "sentence_count": config["sentence_count"],
            "vocab_level": config["vocab_level"]
        }
    
    # 초기 대화인 경우 initial_talking_prompt 사용
    if initial:
        chain = (
            process_talking_input
            | initial_talking_prompt
            | llm
            | StrOutputParser()
        )
    else:
        chain = (
            process_talking_input
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
    """BERT 기반 CEFR 평가"""
    print("Using BERT for CEFR evaluation")
    
    # BERT 평가를 Langchain Runnable로 변환
    bert_evaluator = RunnableLambda(
        lambda x: evaluate_last_message_cefr(x.get("chat_history", []))
    )
    
    rag_with_history = RunnableWithMessageHistory(
        bert_evaluator,
        get_message_history,
        input_messages_key="question",
        history_messages_key="chat_history",
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
