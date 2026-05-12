from pinecone import Pinecone, ServerlessSpec
from app.config import settings

class _UnavailableCollection:
    def __init__(self, reason: str):
        self.reason = reason

    def _raise(self):
        raise RuntimeError(self.reason)

    def delete(self, *args, **kwargs):
        self._raise()

    def upsert(self, *args, **kwargs):
        self._raise()

    def query(self, *args, **kwargs):
        self._raise()


collection = None

if not settings.PINECONE_API_KEY:
    collection = _UnavailableCollection("PINECONE_API_KEY is not configured. Add it to backend .env.")
elif not settings.PINECONE_ENV:
    collection = _UnavailableCollection("PINECONE_ENV is not configured. Add your Pinecone region to backend .env.")
else:
    # Initialize Pinecone client
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    # Ensure the index exists
    if settings.PINECONE_INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.PINECONE_ENV,
            ),
        )

    # Connect to the index
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    collection = index
