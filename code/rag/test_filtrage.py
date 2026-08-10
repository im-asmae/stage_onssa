from rag.retriever import Retriever


retriever = Retriever()


questions = [
    "Quels sont les ravageurs du rosier ?",
    "Quels sont les ravageurs du bananier ?",
    "Quels sont les traitements prévus sur l'oranger ?",
]


for question in questions:

    print("\n" + "=" * 70)

    print("QUESTION :", question)

    results = retriever.retrieve(
        query=question,
        k=5
    )

    if not results:
        print("Aucun résultat.")
        continue

    for result in results:

        metadata = result["metadata"]

        print(
            f"{metadata.get('culture')} | "
            f"{metadata.get('section')} | "
            f"distance={result['distance']}"
        )