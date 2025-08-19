from langchain_community.retrievers import BM25Retriever
from src.v2.ebook_loader import load_ebook, load_context

def load_retriever(book_id):
    return BM25Retriever.from_documents(
        load_ebook(book_id),
        k=10
    )

def load_full_context(book_id):
    return BM25Retriever.from_texts(
        [load_context(book_id)],
        k=1
    )
