from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def health():
    return {"status": "hello world"}


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(reply=f"echo: {request.message}")
