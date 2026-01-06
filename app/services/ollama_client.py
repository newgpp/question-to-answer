import requests
from app.config import OLLAMA_HOST, EMBED_MODEL

def embed(text: str) -> list[float]:
    r = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]