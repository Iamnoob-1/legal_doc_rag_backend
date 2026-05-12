from sentence_transformers import SentenceTransformer, CrossEncoder

# Cache all models inside ./models
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2", cache_folder="./models"
)

legal_model = SentenceTransformer(
    "nlpaueb/legal-bert-base-uncased", cache_folder="./models"
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2", cache_folder="./models"
)
