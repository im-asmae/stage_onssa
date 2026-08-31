# from rag.retriever import Retriever


# def test_pucerons_retrieval():

#     print("=" * 70)
#     print("TEST — CULTURES ASSOCIÉES AUX PUCERONS")
#     print("=" * 70)

#     question = "Quelles cultures sont sensibles aux pucerons ?"

#     print(f"\nQuestion : {question}")

#     print("\nInitialisation du Retriever...")
#     retriever = Retriever()

#     print("\nRecherche...")
#     results = retriever.retrieve(
#         query=question,
#         k=10
#     )

#     print("\n" + "=" * 70)
#     print("RÉSULTATS RÉCUPÉRÉS")
#     print("=" * 70)

#     if not results:
#         print("❌ Aucun résultat récupéré.")
#         return

#     cultures = set()

#     for i, result in enumerate(results, start=1):

#         metadata = result["metadata"]

#         culture = metadata.get("culture")
#         section = metadata.get("section")

#         if culture:
#             cultures.add(culture)

#         print(f"\n--- Chunk {i} ---")
#         print(f"Culture  : {culture}")
#         print(f"Section  : {section}")
#         print(f"Distance : {result['distance']}")
#         print(f"Score    : {result.get('rerank_score')}")

#     print("\n" + "=" * 70)
#     print("CULTURES RÉCUPÉRÉES")
#     print("=" * 70)

#     for culture in sorted(cultures):
#         print(f"✓ {culture}")

#     print(f"\nNombre de cultures récupérées : {len(cultures)}")

#     print("\n" + "=" * 70)
#     print("FIN DU TEST")
#     print("=" * 70)


# if __name__ == "__main__":
#     test_pucerons_retrieval()

from rag.retriever import Retriever
from rag.llm import LLM


def print_separator():
    print("\n" + "=" * 70)


def test_t09():

    print_separator()
    print("TEST T09 — GÉNÉRATION LLM AVEC CONTEXTE FILTRÉ")
    print_separator()

    retriever = Retriever()
    llm = LLM()

    tests = [

        # ==========================================================
        # TEST 1
        # ==========================================================
        {
            "name": "Ravageurs du bananier",
            "question": "Quels sont les ravageurs du bananier ?",
            "expected": [
                "Nématodes",
                "Acariens",
                "Mouches blanches",
                "Noctuelles défoliatrices"
            ],
            "mode": "culture_section"
        },

        # ==========================================================
        # TEST 2
        # ==========================================================
        {
            "name": "Ravageurs du fraisier",
            "question": "Quels sont les ravageurs du fraisier ?",
            "expected": [
                "Nématodes",
                "Acariens",
                "Mouches blanches",
                "Drosophila suzukii",
                "Noctuelles défoliatrices",
                "Pucerons",
                "Thrips"
            ],
            "mode": "culture_section"
        },

        # ==========================================================
        # TEST 3
        # ==========================================================
        {
            "name": "Maladies du bananier",
            "question": "Quelles sont les maladies du bananier ?",
            "expected": [
                # À ADAPTER selon le contenu exact du chunk
            ],
            "mode": "culture_section"
        },

        # ==========================================================
        # TEST 4
        # ==========================================================
        {
            "name": "Adventices des blés",
            "question": "Quels sont les adventices des blés ?",
            "expected": [
                # À ADAPTER selon le chunk exact
            ],
            "mode": "culture_section"
        },

        # ==========================================================
        # TEST 5
        # ==========================================================
        {
            "name": "Cultures sensibles aux pucerons",
            "question": "Quelles cultures sont sensibles aux pucerons ?",
            "expected": [
                "Abricotier",
                "Amandier",
                "Artichaut",
                "Aubergine",
                "Blé dur",
                "Blé tendre",
                "Carotte",
                "Fraisier",
                "Maïs",
                "Menthe",
                "Oranger",
                "Orge",
                "Piment",
                "Poivron",
                "Pommier",
                "Rosier",
                "Tomate",
                "Triticale"
            ],
            "mode": "target"
        },

        # ==========================================================
        # TEST 6
        # ==========================================================
        {
            "name": "Question hors référentiel",
            "question": "Quelle est la couleur préférée des agriculteurs marocains ?",
            "expected": [],
            "mode": "normal"
        }
    ]

    passed = 0

    for index, test in enumerate(tests, start=1):

        print_separator()
        print(f"TEST {index} — {test['name']}")
        print_separator()

        question = test["question"]

        print(f"\nQuestion : {question}")

        # ==========================================================
        # RETRIEVAL
        # ==========================================================

        print("\nRecherche du contexte...")

        if test["mode"] == "target":

            detected_target = retriever.detect_target(question)

            print("\nCible détectée :")
            print(detected_target)

            if detected_target["status"] == "FOUND":

                chunks = retriever.retrieve_by_target(
                    detected_target["target"]
                )

            else:

                chunks = []

        else:

            chunks = retriever.retrieve(
                question,
                k=10
            )

        print(f"\nNombre de chunks : {len(chunks)}")

        # ==========================================================
        # CONTEXTE
        # ==========================================================

        context = retriever.format_context(chunks)

        print("\nCONTEXTE ENVOYÉ AU LLM")
        print("-" * 70)

        # Pour éviter un terminal gigantesque
        if len(context) > 12000:

            print(context[:12000])
            print("\n...[CONTEXTE TRONQUÉ POUR L'AFFICHAGE]...")

        else:

            print(context)

        # ==========================================================
        # LLM
        # ==========================================================

        print("\nGénération de la réponse...")

        response = llm.generate(
            question=question,
            context=context
        )

        print("\nRÉPONSE DU LLM")
        print("-" * 70)
        print(response)

        # ==========================================================
        # VÉRIFICATION
        # ==========================================================

        response_normalized = retriever._normalize_text(
            response
        )

        found = 0
        missing = []

        for expected in test["expected"]:

            expected_normalized = retriever._normalize_text(
                expected
            )

            if expected_normalized in response_normalized:

                print(f"✓ {expected}")
                found += 1

            else:

                print(f"✗ {expected}")
                missing.append(expected)

        # ==========================================================
        # SCORE
        # ==========================================================

        if len(test["expected"]) == 0:

            # Pour une question hors référentiel,
            # on vérifie simplement que le modèle ne donne
            # pas une réponse inventée.
            suspicious = [
                "agriculteurs marocains",
                "couleur préférée"
            ]

            hallucination = any(
                word in response_normalized
                for word in suspicious
            )

            if not hallucination:

                print("\n✓ Réponse hors référentiel correctement gérée")
                passed += 1

            else:

                print("\n✗ Risque de réponse inventée")

            continue

        score = (
            found /
            len(test["expected"])
        ) * 100

        print("\n" + "-" * 70)
        print(f"Score : {score:.2f}%")

        if missing:

            print("\nÉléments manquants :")

            for item in missing:

                print(f"  ✗ {item}")

        else:

            print("\n✓ Tous les éléments attendus sont présents.")

        if score == 100:

            passed += 1

    # ==============================================================
    # RÉSULTAT FINAL
    # ==============================================================

    print_separator()
    print("RÉSULTAT FINAL T09")
    print_separator()

    total = len(tests)

    score = (
        passed /
        total
    ) * 100

    print(f"\nTests réussis : {passed}/{total}")
    print(f"Score global : {score:.2f}%")

    if passed == total:

        print("\n✓ T09 RÉUSSI — Génération LLM correcte.")

    else:

        print("\n⚠ T09 — Certains tests échouent.")

    print_separator()


if __name__ == "__main__":
    test_t09()