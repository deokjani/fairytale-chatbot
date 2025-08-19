from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.v3.router import router_v3

app = FastAPI(
    docs_url="/v3/book/docs",
    redoc_url="/v3/book/redoc", 
    openapi_url="/v3/book/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_v3)