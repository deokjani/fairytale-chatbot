import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")

# BERT CEFR Model (from env)
BERT_CEFR_MODEL = os.getenv("BERT_CEFR_MODEL", "AbdulSami/bert-base-cased-cefr")
