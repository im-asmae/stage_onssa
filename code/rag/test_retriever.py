from rag.retriever import Retriever
from rag.llm import LLM 

retriever = Retriever()

query = "Quels sont les ravageurs du rosier ?"

print("=" * 80)
print("QUESTION")
print(query)

print("\n" + "=" * 80)
print("RECHERCHE GLOBALE")
print("=" * 80)

results = retriever.retrieve(
    query=query,
    k=5
)

for i, chunk in enumerate(results, start=1):

    meta = chunk["metadata"]

    print(f"\nRésultat {i}")
    print(f"Famille : {meta['family']}")
    print(f"Culture : {meta['culture']}")
    print(f"Section : {meta['section']}")
    print(f"Page    : {meta['page']}")
    print("Distance :", chunk["distance"])
    print("-" * 60)
    print(chunk["text"][:500])
    print("-" * 60)


print("\n")
print("=" * 80)
print("RECHERCHE FILTRÉE (Culture = Oranger)")
print("=" * 80)



results = retriever.retrieve(
    query=query,
    culture="Oranger",
    k=5
)

# On ne garde que les 3 meilleurs chunks
context = retriever.format_context(results[:3])

llm=LLM()
answer = llm.generate(
    question=query,
    context=context
)

print(answer)

if not results:

    print("Aucun résultat.")

else:

    for i, chunk in enumerate(results, start=1):

        meta = chunk["metadata"]

        print(f"\nRésultat {i}")
        print(f"Famille : {meta['family']}")
        print(f"Culture : {meta['culture']}")
        print(f"Section : {meta.get('section')}")
        print(f"Page    : {meta['page']}")
        print("Distance :", chunk["distance"])

        if "rerank_score" in chunk:
            print("Rerank :", chunk["rerank_score"])

        print("-" * 60)
        print(chunk["text"][:500])
        print("-" * 60)


print("\n")
print("=" * 80)
print("CONTEXTE ENVOYÉ AU LLM")
print("=" * 80)

context = retriever.format_context(results)

print(context)