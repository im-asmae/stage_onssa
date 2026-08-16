import json

from parser.models import Chunk
from rag.embedder import Embedder
from rag.vector_store import VectorStore


# Chargement des chunks
with open("C:/Users/HP/Desktop/stage_onssa/code/parser/chunks.json", encoding="utf-8") as f:
    data = json.load(f)

chunks = []

for item in data:

    chunk = Chunk(
        id=item["id"],
        culture=item["culture"],
        text=item["text"],
        metadata=item["metadata"]
    )

    chunks.append(chunk)


print(f"{len(chunks)} chunks chargés.")


embedder = Embedder()

store = VectorStore()

store.reset()

store.add_chunks(
    chunks,
    embedder
)

print()

print("Nombre de documents dans ChromaDB :")

print(store.count())