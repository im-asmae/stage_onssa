import time
from collections import Counter

from rag.retriever import Retriever
from rag.llm import LLM


# ============================================================
# CONFIGURATION
# ============================================================

K = 5

TESTS = [

    {
        "id": "T01",
        "category": "Recherche directe",
        "question": "Quels sont les ravageurs du rosier ?",
        "expected_culture": "Rosier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices",
            "Cochenilles",
            "Pucerons",
            "Insectes",
        ],
    },

    {
        "id": "T02",
        "category": "Question ciblée",
        "question": "Quels traitements sont prévus contre les mouches blanches sur le rosier ?",
        "expected_culture": "Rosier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Mouches blanches",
            "Parties aériennes",
        ],
    },

    {
        "id": "T03",
        "category": "Recherche de traitements",
        "question": "Quels traitements sont prévus sur l'oranger ?",
        "expected_culture": "Oranger",
        "expected_section": None,
        "expected_keywords": [
            "Ravageurs",
            "Maladies",
        ],
    },

    {
        "id": "T04",
        "category": "Changement de culture",
        "question": "Quels sont les ravageurs du bananier ?",
        "expected_culture": "Bananier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices",
        ],
    },

    {
        "id": "T05",
        "category": "Question ciblée",
        "question": "Quels sont les ravageurs du fraisier ?",
        "expected_culture": "Fraisier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Drosophila suzukii",
            "Noctuelles défoliatrices",
            "Pucerons",
            "Thrips",
        ],
    },

    {
        "id": "T06",
        "category": "Changement de culture",
        "question": "Quels ravageurs sont concernés par des traitements sur le bananier ?",
        "expected_culture": "Bananier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices",
        ],
    },

    {
        "id": "T07",
        "category": "Information absente",
        "question": "Quels traitements sont prévus contre les pucerons sur le bananier ?",
        "expected_culture": "Bananier",
        "expected_section": "Ravageurs",
        "expected_keywords": [],
        "expected_absent": True,
    },

    {
        "id": "T08",
        "category": "Changement de section",
        "question": "Quelles maladies sont traitées sur le rosier ?",
        "expected_culture": "Rosier",
        "expected_section": "Maladies",
        "expected_keywords": [
            "Maladie des taches noires",
            "Mildiou",
            "Oïdium",
            "Pourriture grise",
            "Rouille",
        ],
    },

    {
        "id": "T09",
        "category": "Changement de section",
        "question": "Quelles sont les maladies du fraisier ?",
        "expected_culture": "Fraisier",
        "expected_section": "Maladies",
        "expected_keywords": [
            "Fusariose",
            "Verticiliose",
            "Mildiou",
            "Oïdium",
            "Pourriture grise",
        ],
    },

    {
        "id": "T10",
        "category": "Changement de section",
        "question": "Quels sont les adventices de l'oranger ?",
        "expected_culture": "Oranger",
        "expected_section": "Adventices",
        "expected_keywords": [
            "Adventices",
            "dicotylédones",
            "graminées",
        ],
    },

    {
        "id": "T11",
        "category": "Robustesse",
        "question": "Quels nuisibles peuvent être traités sur le rosier ?",
        "expected_culture": "Rosier",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices",
            "Cochenilles",
            "Pucerons",
        ],
    },

    {
        "id": "T12",
        "category": "Paraphrase",
        "question": "Quels insectes et autres ravageurs font l'objet de traitements sur l'oranger ?",
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Pucerons",
        ],
    },

    {
        "id": "T13",
        "category": "Relation culture-cible-usage",
        "question": "Quels ravageurs de l'oranger sont traités sur les parties aériennes ?",
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Insectes xylophages",
            "Mineuses des feuilles",
            "Pucerons",
        ],
    },

    {
        "id": "T14",
        "category": "Relation usage-cible",
        "question": "Quel ravageur de l'oranger est traité au niveau du sol ?",
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
        "expected_keywords": [
            "Nématodes",
            "Traitement du sol",
        ],
    },

    {
        "id": "T15",
        "category": "Hors domaine",
        "question": "Quelle est la capitale du Maroc ?",
        "expected_culture": None,
        "expected_section": None,
        "expected_keywords": [],
        "expected_absent": True,
    },
]


# ============================================================
# OUTILS
# ============================================================

def normalize(text):
    if text is None:
        return ""

    return text.lower().strip()


def calculate_keyword_score(answer, keywords):

    if not keywords:
        return None

    answer_lower = normalize(answer)

    found = []
    missing = []

    for keyword in keywords:

        if normalize(keyword) in answer_lower:
            found.append(keyword)
        else:
            missing.append(keyword)

    score = len(found) / len(keywords) * 100

    return {
        "score": round(score, 2),
        "found": found,
        "missing": missing,
    }


def get_retrieved_cultures(results):

    cultures = []

    for result in results:

        culture = result["metadata"].get("culture")

        if culture:
            cultures.append(culture)

    return cultures


def get_retrieved_sections(results):

    sections = []

    for result in results:

        section = result["metadata"].get("section")

        if section:
            sections.append(section)

    return sections


def detect_contamination(results, expected_culture):

    if not expected_culture:
        return False, []

    cultures = get_retrieved_cultures(results)

    foreign = [
        culture
        for culture in cultures
        if normalize(culture) != normalize(expected_culture)
    ]

    return len(foreign) > 0, foreign


# ============================================================
# EXECUTION
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("       BATTERIE DE TESTS GLOBALE V2 — AGENT RAG ONSSA")
    print("=" * 70)

    retriever = Retriever()
    llm = LLM()

    results_report = []

    for test in TESTS:

        print("\n")
        print("=" * 70)
        print(f"{test['id']} — {test['category']}")
        print("=" * 70)

        question = test["question"]

        print(f"\nQuestion : {question}")

        start_time = time.time()

        try:

            # ------------------------------------------------
            # RETRIEVAL
            # ------------------------------------------------

            retrieved = retriever.retrieve(
                query=question,
                k=K
            )

            # ------------------------------------------------
            # ANALYSE RETRIEVAL
            # ------------------------------------------------

            cultures = get_retrieved_cultures(retrieved)
            sections = get_retrieved_sections(retrieved)

            contamination, foreign_cultures = detect_contamination(
                retrieved,
                test["expected_culture"]
            )

            # ------------------------------------------------
            # CONTEXT
            # ------------------------------------------------

            context = retriever.format_context(
                retrieved[:2]
            )

            # ------------------------------------------------
            # GENERATION
            # ------------------------------------------------

            answer = llm.generate(
                question=question,
                context=context
            )

            elapsed = time.time() - start_time

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            keyword_result = calculate_keyword_score(
                answer,
                test["expected_keywords"]
            )

            # ------------------------------------------------
            # DETECTION CULTURE
            # ------------------------------------------------

            detected_culture = retriever.detect_culture(
                question
            )

            if detected_culture:

                detected_culture_name = detected_culture["culture"]

            else:

                detected_culture_name = None

            # ------------------------------------------------
            # STATUT
            # ------------------------------------------------

            if test.get("expected_absent"):

                # Pour les informations absentes,
                # on ne donne pas encore de score strict.

                status = "REVIEW"

            elif keyword_result:

                score = keyword_result["score"]

                if score >= 90 and not contamination:
                    status = "PASS"

                elif score >= 50:
                    status = "REVIEW"

                else:
                    status = "FAIL"

            else:

                status = "REVIEW"

            # ------------------------------------------------
            # AFFICHAGE
            # ------------------------------------------------

            print("\nCulture détectée :")
            print(f"  {detected_culture_name}")

            print("\nCultures récupérées :")

            culture_counts = Counter(cultures)

            for culture, count in culture_counts.items():
                print(f"  - {culture} : {count}")

            print("\nSections récupérées :")

            section_counts = Counter(sections)

            for section, count in section_counts.items():
                print(f"  - {section} : {count}")

            print("\nContamination inter-culture :")

            if contamination:

                print("  OUI")

                print("  Cultures étrangères :")

                for culture in foreign_cultures:
                    print(f"    - {culture}")

            else:

                print("  NON")

            print("\nChunks récupérés :")

            for i, chunk in enumerate(retrieved, start=1):

                metadata = chunk["metadata"]

                print(
                    f"  {i}. "
                    f"{metadata.get('culture')} | "
                    f"{metadata.get('section')} | "
                    f"distance={chunk['distance']}"
                )

            print("\nRéponse :")
            print(answer)

            if keyword_result:

                print("\nScore mots-clés :")
                print(f"  {keyword_result['score']}%")

                if keyword_result["missing"]:

                    print("  Mots-clés manquants :")

                    for keyword in keyword_result["missing"]:
                        print(f"    - {keyword}")

            else:

                print("\nScore mots-clés : N/A")

            print(f"\nTemps : {elapsed:.2f}s")

            print(f"\nSTATUT : {status}")

            # ------------------------------------------------
            # SAUVEGARDE
            # ------------------------------------------------

            results_report.append({

                "id": test["id"],
                "category": test["category"],
                "question": question,

                "expected_culture":
                    test["expected_culture"],

                "detected_culture":
                    detected_culture_name,

                "retrieved_cultures":
                    list(culture_counts.keys()),

                "retrieved_sections":
                    list(section_counts.keys()),

                "contamination":
                    contamination,

                "foreign_cultures":
                    foreign_cultures,

                "keyword_score":
                    keyword_result["score"]
                    if keyword_result
                    else None,

                "missing_keywords":
                    keyword_result["missing"]
                    if keyword_result
                    else [],

                "status":
                    status,

                "time":
                    round(elapsed, 2),

                "answer":
                    answer
            })

        except Exception as e:

            print("\nERREUR TECHNIQUE :")
            print(e)

            results_report.append({

                "id": test["id"],
                "category": test["category"],
                "question": question,
                "status": "ERROR",
                "error": str(e)
            })


    # ========================================================
    # RAPPORT FINAL
    # ========================================================

    print("\n\n")
    print("=" * 70)
    print("                    RAPPORT GLOBAL V2")
    print("=" * 70)

    total = len(results_report)

    passed = sum(
        1
        for r in results_report
        if r["status"] == "PASS"
    )

    review = sum(
        1
        for r in results_report
        if r["status"] == "REVIEW"
    )

    failed = sum(
        1
        for r in results_report
        if r["status"] == "FAIL"
    )

    errors = sum(
        1
        for r in results_report
        if r["status"] == "ERROR"
    )

    contaminated = sum(
        1
        for r in results_report
        if r.get("contamination") is True
    )

    scored = [
        r["keyword_score"]
        for r in results_report
        if r.get("keyword_score") is not None
    ]

    times = [
        r["time"]
        for r in results_report
        if r.get("time") is not None
    ]

    print(f"\nNombre total de tests : {total}")

    print(f"PASS : {passed}")
    print(f"REVIEW : {review}")
    print(f"FAIL : {failed}")
    print(f"ERROR : {errors}")

    if total:

        print(
            f"\nTaux de réussite strict : "
            f"{passed / total * 100:.2f}%"
        )

    if scored:

        print(
            f"Score moyen mots-clés : "
            f"{sum(scored) / len(scored):.2f}%"
        )

    if times:

        print(
            f"Temps moyen : "
            f"{sum(times) / len(times):.2f}s"
        )

    print(
        f"Tests avec contamination inter-culture : "
        f"{contaminated}"
    )

    # ========================================================
    # TABLEAU
    # ========================================================

    print("\n")
    print("-" * 100)

    print(
        f"{'ID':<5}"
        f"{'Catégorie':<28}"
        f"{'Score':<10}"
        f"{'Culture':<15}"
        f"{'Contam.':<10}"
        f"{'Statut':<10}"
    )

    print("-" * 100)

    for r in results_report:

        score = r.get("keyword_score")

        score_text = (
            f"{score:.2f}%"
            if score is not None
            else "N/A"
        )

        culture = r.get(
            "detected_culture",
            "None"
        )

        contamination_text = (
            "OUI"
            if r.get("contamination")
            else "NON"
        )

        print(
            f"{r['id']:<5}"
            f"{r['category'][:27]:<28}"
            f"{score_text:<10}"
            f"{str(culture)[:14]:<15}"
            f"{contamination_text:<10}"
            f"{r['status']:<10}"
        )

    print("-" * 100)

    # ========================================================
    # PROBLEMES A ANALYSER
    # ========================================================

    print("\n")
    print("=" * 70)
    print("                  POINTS À ANALYSER")
    print("=" * 70)

    print("\n1. CONTAMINATION INTER-CULTURE")

    contaminated_tests = [
        r for r in results_report
        if r.get("contamination")
    ]

    if contaminated_tests:

        for r in contaminated_tests:

            print(
                f"\n{r['id']} : "
                f"{r['question']}"
            )

            print(
                f"Culture attendue : "
                f"{r.get('expected_culture')}"
            )

            print(
                f"Cultures étrangères : "
                f"{r.get('foreign_cultures')}"
            )

    else:

        print("Aucune contamination détectée.")

    print("\n2. TESTS À REVOIR")

    review_tests = [
        r for r in results_report
        if r["status"] in ["REVIEW", "FAIL"]
    ]

    if review_tests:

        for r in review_tests:

            print(
                f"\n{r['id']} — "
                f"{r['question']}"
            )

            print(
                f"Statut : {r['status']}"
            )

            print(
                f"Score : "
                f"{r.get('keyword_score', 'N/A')}"
            )

            print(
                f"Sections : "
                f"{r.get('retrieved_sections')}"
            )

            print(
                f"Culture(s) récupérée(s) : "
                f"{r.get('retrieved_cultures')}"
            )

    else:

        print("Aucun test à revoir.")

    print("\n")
    print("=" * 70)
    print("                 FIN DES TESTS V2")
    print("=" * 70)


if __name__ == "__main__":
    main()