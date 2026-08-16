from rag.vector_store import VectorStore


def test_pucerons_extraction():

    print("=" * 70)
    print("TEST — EXTRACTION DES CULTURES CONTENANT 'PUCERONS'")
    print("=" * 70)

    vector_store = VectorStore()

    print("\nRécupération des données depuis ChromaDB...")

    # Récupérer tous les documents et métadonnées
    data = vector_store.collection.get(
        include=["documents", "metadatas"]
    )

    documents = data["documents"]
    metadatas = data["metadatas"]

    cultures = set()

    for document, metadata in zip(documents, metadatas):

        if "pucerons" in document.lower():

            culture = metadata.get("culture")

            if culture:
                cultures.add(culture)

    cultures = sorted(cultures)

    print("\n" + "=" * 70)
    print("CULTURES CONTENANT 'PUCERONS'")
    print("=" * 70)

    for culture in cultures:
        print(f"✓ {culture}")

    print("\n" + "=" * 70)
    print(f"Nombre de cultures : {len(cultures)}")
    print("=" * 70)


if __name__ == "__main__":
    test_pucerons_extraction()