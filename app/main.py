from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.config import TOP_K, MIN_SCORE
from app.services.qdrant_store import search

app = FastAPI()


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=TOP_K, ge=1, le=20)
    province: Optional[str] = None
    biz_line: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/answer")
def answer(req: AnswerRequest) -> Dict[str, Any]:
    hits = search(
        question=req.question,
        top_k=req.top_k,
        province=req.province,
        biz_line=req.biz_line
    )

    hits = [h for h in hits if h.get("score", 0.0) >= MIN_SCORE]

    return {
        "question": req.question,
        "top_k": req.top_k,
        "filters": {"province": req.province, "biz_line": req.biz_line},
        "hits": hits
    }

