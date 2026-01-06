from app.policy_docs import DOCS
from app.services.qdrant_store import ingest_policy_docs

if __name__ == "__main__":
    ingest_policy_docs(DOCS)
    print("ingest done")
