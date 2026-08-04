from rag.retriever import Retriever

retriever = Retriever()

query = "Comment traiter les pucerons du oranger ?"

print("=" * 80)
print("QUESTION")
print(query)

print("\n" + "=" * 80)
print("RECHERCHE GLOBALE")
print("=" * 80)

results = retriever.retrieve(query, k=5)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
ids = results["ids"][0]
distances = results["distances"][0]

for i, (doc, meta, chunk_id, dist) in enumerate(
    zip(documents, metadatas, ids, distances),
    start=1
):
    print(f"\nRésultat {i}")
    print(f"ID       : {chunk_id}")
    print(f"Culture  : {meta['culture']}")
    print(f"Famille  : {meta['family']}")
    print(f"Page     : {meta['page']}")
    print(f"Distance : {dist:.4f}")
    print("-" * 60)
    print(doc[:350], "...")
    print("-" * 60)


print("\n\n")
print("=" * 80)
print("RECHERCHE FILTRÉE (Culture = Oranger)")
print("=" * 80)

results = retriever.retrieve_by_culture(
    culture="Oranger",
    query=query,
    k=5
)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
ids = results["ids"][0]
distances = results["distances"][0]

if len(documents) == 0:
    print("Aucun résultat.")
else:

    for i, (doc, meta, chunk_id, dist) in enumerate(
        zip(documents, metadatas, ids, distances),
        start=1
    ):
        print(f"\nRésultat {i}")
        print(f"ID       : {chunk_id}")
        print(f"Culture  : {meta['culture']}")
        print(f"Famille  : {meta['family']}")
        print(f"Page     : {meta['page']}")
        print(f"Distance : {dist:.4f}")
        print("-" * 60)
        print(doc[:350], "...")
        print("-" * 60)