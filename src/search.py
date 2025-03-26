from src.db import db
from src.embeddings import embeddings


class Search:
    @staticmethod
    def semantic_search(query: str):
        emb = embeddings.encode(query)
        return db.semantic_search(emb)
