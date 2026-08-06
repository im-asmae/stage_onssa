import json

from parser.models import Chunk
from rag.keyword_store import KeywordStore


# ==========================================================
# Chargement des chunks
# ==========================================================

with open(
    "C:/Users/HP/Desktop/stage_onssa/code/parser/chunks_v2.json",
    encoding="utf-8"
) as f:
    data = json.load(f)


chunks = []

for item in data:

    chunks.append(
        Chunk(
            id=item["id"],
            culture=item["culture"],
            text=item["text"],
            metadata=item["metadata"]
        )
    )


print(f"{len(chunks)} chunks chargés.")


# ==========================================================
# Création de l'index Whoosh
# ==========================================================

store = KeywordStore()

store.reset()

store.add_chunks(chunks)

print("\nIndex Whoosh créé avec succès.")
print(f"Nombre de documents : {store.index.doc_count()}")


# ==========================================================
# Tests
# ==========================================================

queries = [
    "pucerons oranger",
    "Comment traiter les pucerons du oranger ?",
    "alternariose oranger",
    "nématodes citronnier",
    "mouches blanches tomate"
]


for query in queries:

    print("\n" + "=" * 80)
    print("REQUÊTE :", query)
    print("=" * 80)

    results = store.search(query, k=5)

    if not results:
        print("Aucun résultat.")
        continue

    for i, r in enumerate(results, start=1):

        print(f"\nRésultat {i}")
        print("ID      :", r["id"])
        print("Famille :", r["metadata"]["family"])
        print("Culture :", r["metadata"]["culture"])
        print("Section :", r["metadata"]["section"])
        print("Score   :", r["score"])

        print("-" * 60)
        print(r["text"][:500])
        print("-" * 60)