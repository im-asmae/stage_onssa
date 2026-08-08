from rag.retriever import Retriever
from rag.llm import LLM


def main():

    retriever = Retriever()
    llm = LLM()

    question = "Comment traiter les pucerons du oranger ?"

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n")
    print("=" * 80)
    print("RECHERCHE")
    print("=" * 80)

    results = retriever.retrieve(
        query=question,
        k=5
    )

    if not results:
        print("Aucun résultat trouvé.")
        return

    # Affichage des résultats récupérés
    for i, chunk in enumerate(results, start=1):

        meta = chunk["metadata"]

        print(f"\nRésultat {i}")
        print(f"Famille : {meta['family']}")
        print(f"Culture : {meta['culture']}")
        print(f"Section : {meta['section']}")
        print(f"Page    : {meta['page']}")
        print(f"Distance : {chunk['distance']:.4f}")

        if "rerank_score" in chunk:
            print(f"Rerank  : {chunk['rerank_score']:.4f}")

    print("\n")
    print("=" * 80)
    print("CONTEXTE ENVOYÉ AU LLM")
    print("=" * 80)

    # On n'envoie que les 3 meilleurs chunks
    context = retriever.format_context(results[:3])

    print(context)

    print("\n")
    print("=" * 80)
    print("RÉPONSE DU LLM")
    print("=" * 80)

    answer = llm.generate(
        question=question,
        context=context
    )

    print(answer)


if __name__ == "__main__":
    main()