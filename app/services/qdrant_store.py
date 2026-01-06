import uuid, requests
from typing import Optional, List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from app.config import QDRANT_URL, QDRANT_COLLECTION
from app.services.ollama_client import embed


client = QdrantClient(url=QDRANT_URL)


def ensure_collection(vector_size: int):
    cols = client.get_collections().collections
    if any(c.name == QDRANT_COLLECTION for c in cols):
        return
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=qm.VectorParams(size=vector_size, distance=qm.Distance.COSINE),
    )


def ingest_policy_docs(docs: list[dict]):
    # 探测维度 + 建 collection（只会建一次）
    dim = len(embed("dimension probe"))
    ensure_collection(dim)

    points = []
    for doc in docs:
        for idx, item in enumerate(doc["items"], 1):
            vec = embed(item)
            points.append(
                qm.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec,
                    payload={
                        "doc_id": doc["doc_id"],
                        "province": doc["province"],
                        "biz_line": doc["biz_line"],
                        "version": doc["version"],
                        "item_no": idx,
                        "text": item,
                    },
                )
            )

    if points:
        client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def search(question: str, top_k: int = 5, province: Optional[str] = None, biz_line: Optional[str] = None) -> List[Dict[str, Any]]:
    qvec = embed(question)

    must = []
    if province:
        must.append({"key": "province", "match": {"value": province}})
    if biz_line:
        must.append({"key": "biz_line", "match": {"value": biz_line}})

    body: Dict[str, Any] = {
        "vector": qvec,
        "limit": top_k,
        "with_payload": True,
    }
    if must:
        body["filter"] = {"must": must}

    url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search"
    r = requests.post(url, json=body, timeout=60)
    r.raise_for_status()

    data = r.json()
    hits = data.get("result", [])

    results = []
    for h in hits:
        p = h.get("payload") or {}
        results.append({
            "score": float(h.get("score", 0.0)),
            "doc_id": p.get("doc_id"),
            "province": p.get("province"),
            "biz_line": p.get("biz_line"),
            "version": p.get("version"),
            "item_no": p.get("item_no"),
            "text": p.get("text"),
        })
    return results
