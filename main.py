import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from storage import store
from llm import process_user_turn

app = FastAPI(title="Family Voice Assistant", version="1.0.0")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    tools_called: List[Dict[str, Any]]
    provider: str
    state: Dict[str, Any]


@app.get("/api/state")
def get_state():
    """Returns current family state (groceries, reminders, events)."""
    return {
        "provider": os.getenv("LLM_PROVIDER", "mock"),
        "state": store.get_state()
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_turn(req: ChatRequest):
    """Processes user voice/text query, executes tools, and returns spoken-style reply."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history_dicts = [{"role": h.role, "content": h.content} for h in (req.history or [])]
    text, tools_called, provider = process_user_turn(req.message, history_dicts)

    return ChatResponse(
        response=text,
        tools_called=tools_called,
        provider=provider,
        state=store.get_state()
    )


# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    """Serves the frontend SPA."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Family Voice Assistant API is running. Missing static/index.html"}
