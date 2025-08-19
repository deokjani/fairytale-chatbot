import json
from langchain_community.document_loaders import JSONLoader

# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    metadata["PAGE_NO"] = record.get("PAGE_NO")
    metadata["PAGE_IMG"] = record.get("PAGE_IMG")

    return metadata

def load_ebook(book_id):
    loader = JSONLoader(
        file_path=f'ebook/{book_id}/common/data/ebook_data.json',
        jq_schema='.PAGE[]',
        content_key="PAGE_TEXT",
        metadata_func=metadata_func
    )
    return loader.load()

def load_context(book_id):
    context = ""
    with open(f'ebook/{book_id}/common/data/ebook_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    context += f'BOOK_NAME: {data["BOOK_NAME"]}'
    for page in data["PAGE"]:
        context += f'{page["PAGE_TEXT"]}\n'

    return context