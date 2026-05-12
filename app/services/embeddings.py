from sentence_transformers import SentenceTransformer, CrossEncoder

# Lazy-load models on first use (not on import) to speed up backend startup
_embedding_model = None
_legal_model = None
_reranker = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("Loading embedding model (first use)...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder="./models")
    return _embedding_model

def get_legal_model():
    global _legal_model
    if _legal_model is None:
        print("Loading legal model (first use)...")
        _legal_model = SentenceTransformer("nlpaueb/legal-bert-base-uncased", cache_folder="./models")
    return _legal_model

def get_reranker():
    global _reranker
    if _reranker is None:
        print("Loading reranker model (first use)...")
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", cache_folder="./models")
    return _reranker

# For backward compatibility
embedding_model = get_embedding_model
legal_model = get_legal_model
reranker = get_reranker
