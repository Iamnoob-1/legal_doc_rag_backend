from app.services.embeddings import get_embedding_model
from app.services.database import collection
from typing import List


def retrieve_and_rerank(query: str, top_k: int = 5) -> List[str]:

    embedding_model = get_embedding_model()

    query_emb = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True,
        namespace="legal-docs",
    )

    candidates = [
        match['metadata']['text']
        for match in results['matches']
    ]

    return candidates