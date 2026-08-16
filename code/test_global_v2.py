import time
import json
import csv
from pathlib import Path
from collections import Counter

from rag.retriever import Retriever
from rag.llm import LLM


# ============================================================
# CONFIGURATION
# ============================================================

K = 5

OUTPUT_DIR = Path("test_results")
OUTPUT_DIR.mkdir(exist_ok=True)

ABSENT_MESSAGE = (
    "Cette information n'est pas présente dans le référentiel ONSSA fourni."
)


# ============================================================
# BATTERIE DE TESTS
# ============================================================

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
    """
    Normalisation simple utilisée pour les comparaisons.
    """

    if text is None:
        return ""

    return text.lower().strip()


def calculate_keyword_score(answer, keywords):
    """
    Calcule le pourcentage de mots-clés attendus présents
    dans la réponse générée.
    """

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
    """
    Retourne les cultures présentes dans les chunks récupérés.
    """

    cultures = []

    for result in results:

        culture = result["metadata"].get("culture")

        if culture:
            cultures.append(culture)

    return cultures


def get_retrieved_sections(results):
    """
    Retourne les sections présentes dans les chunks récupérés.
    """

    sections = []

    for result in results:

        section = result["metadata"].get("section")

        if section:
            sections.append(section)

    return sections


def detect_contamination(results, expected_culture):
    """
    Détecte la présence de cultures étrangères dans les résultats.
    """

    if not expected_culture:
        return False, []

    cultures = get_retrieved_cultures(results)

    foreign = [
        culture
        for culture in cultures
        if normalize(culture) != normalize(expected_culture)
    ]

    return len(foreign) > 0, foreign


def detect_expected_section(results, expected_section):
    """
    Vérifie si la section attendue apparaît dans les résultats.
    """

    if not expected_section:
        return True

    sections = get_retrieved_sections(results)

    return any(
        normalize(section) == normalize(expected_section)
        for section in sections
    )


def determine_status(
    test,
    answer,
    keyword_result,
    contamination
):
    """
    Détermine le statut final du test.
    """

    # --------------------------------------------------------
    # Test d'information absente
    # --------------------------------------------------------

    if test.get("expected_absent"):

        if normalize(ABSENT_MESSAGE) in normalize(answer):
            return "PASS"

        return "FAIL"

    # --------------------------------------------------------
    # Tests avec mots-clés attendus
    # --------------------------------------------------------

    if keyword_result:

        score = keyword_result["score"]

        if score >= 90 and not contamination:
            return "PASS"

        elif score >= 50:
            return "REVIEW"

        else:
            return "FAIL"

    # --------------------------------------------------------
    # Cas sans critère automatique
    # --------------------------------------------------------

    return "REVIEW"


# ============================================================
# SAUVEGARDE DES RAPPORTS
# ============================================================

def save_json_report(results_report):

    path = OUTPUT_DIR / "global_test_details.json"

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            results_report,
            f,
            ensure_ascii=False,
            indent=4
        )

    return path


def save_csv_report(results_report):

    path = OUTPUT_DIR / "global_test_summary.csv"

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(
            f,
            delimiter=";"
        )

        writer.writerow([
            "ID",
            "Catégorie",
            "Question",
            "Culture attendue",
            "Culture détectée",
            "Sections récupérées",
            "Contamination",
            "Score mots-clés",
            "Mots-clés manquants",
            "Statut",
            "Temps (s)"
        ])

        for r in results_report:

            writer.writerow([
                r.get("id"),
                r.get("category"),
                r.get("question"),
                r.get("expected_culture"),
                r.get("detected_culture"),
                ", ".join(
                    r.get("retrieved_sections", [])
                ),
                "OUI"
                if r.get("contamination")
                else "NON",
                r.get("keyword_score"),
                ", ".join(
                    r.get("missing_keywords", [])
                ),
                r.get("status"),
                r.get("time")
            ])

    return path


def save_text_report(
    results_report,
    total,
    passed,
    review,
    failed,
    errors,
    contaminated,
    scored,
    times
):

    path = OUTPUT_DIR / "global_test_summary.txt"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "BATTERIE DE TESTS FONCTIONNELS — "
            "AGENT RAG ONSSA\n"
        )

        f.write("=" * 70 + "\n\n")

        f.write(
            f"Nombre total de tests : {total}\n"
        )

        f.write(
            f"Tests réussis : {passed}\n"
        )

        f.write(
            f"Tests à revoir : {review}\n"
        )

        f.write(
            f"Tests en échec : {failed}\n"
        )

        f.write(
            f"Erreurs techniques : {errors}\n"
        )

        f.write(
            f"Contamination inter-culture : "
            f"{contaminated}\n"
        )

        if total:

            f.write(
                f"Taux de réussite strict : "
                f"{passed / total * 100:.2f}%\n"
            )

        if scored:

            f.write(
                f"Score moyen mots-clés : "
                f"{sum(scored) / len(scored):.2f}%\n"
            )

        if times:

            f.write(
                f"Temps moyen de réponse : "
                f"{sum(times) / len(times):.2f}s\n"
            )

        f.write("\n")
        f.write("=" * 70 + "\n")
        f.write("DETAIL DES TESTS\n")
        f.write("=" * 70 + "\n\n")

        for r in results_report:

            f.write(
                f"{r.get('id')} — "
                f"{r.get('category')} — "
                f"{r.get('status')}\n"
            )

            f.write(
                f"Question : "
                f"{r.get('question')}\n"
            )

            f.write(
                f"Culture attendue : "
                f"{r.get('expected_culture')}\n"
            )

            f.write(
                f"Culture détectée : "
                f"{r.get('detected_culture')}\n"
            )

            f.write(
                f"Sections récupérées : "
                f"{r.get('retrieved_sections')}\n"
            )

            f.write(
                f"Contamination : "
                f"{'OUI' if r.get('contamination') else 'NON'}\n"
            )

            f.write(
                f"Score mots-clés : "
                f"{r.get('keyword_score', 'N/A')}\n"
            )

            if r.get("missing_keywords"):

                f.write(
                    "Mots-clés manquants : "
                    + ", ".join(
                        r["missing_keywords"]
                    )
                    + "\n"
                )

            f.write(
                f"Temps : "
                f"{r.get('time', 'N/A')} s\n"
            )

            f.write("\n")

    return path


# ============================================================
# EXECUTION PRINCIPALE
# ============================================================

def main():

    print("\n")

    print("=" * 70)

    print(
        "       BATTERIE DE TESTS GLOBALE — AGENT RAG ONSSA"
    )

    print("=" * 70)

    print(
        f"\nNombre de scénarios : {len(TESTS)}"
    )

    print(
        f"Nombre de résultats par requête : K={K}"
    )

    print(
        f"Dossier des rapports : {OUTPUT_DIR}"
    )


    # --------------------------------------------------------
    # Initialisation
    # --------------------------------------------------------

    print("\nInitialisation du Retriever...")

    retriever = Retriever()

    print("Initialisation du LLM...")

    llm = LLM()

    print("Initialisation terminée.")


    results_report = []


    # ========================================================
    # EXECUTION DES TESTS
    # ========================================================

    for test in TESTS:

        print("\n")
        print("=" * 70)

        print(
            f"{test['id']} — "
            f"{test['category']}"
        )

        print("=" * 70)

        question = test["question"]

        print(
            f"\nQuestion : {question}"
        )

        start_time = time.time()


        try:

            # ------------------------------------------------
            # 1. RETRIEVAL
            # ------------------------------------------------

            retrieved = retriever.retrieve(
                query=question,
                k=K
            )


            # ------------------------------------------------
            # 2. ANALYSE RETRIEVAL
            # ------------------------------------------------

            cultures = get_retrieved_cultures(
                retrieved
            )

            sections = get_retrieved_sections(
                retrieved
            )


            culture_counts = Counter(
                cultures
            )

            section_counts = Counter(
                sections
            )


            # ------------------------------------------------
            # 3. CONTAMINATION
            # ------------------------------------------------

            contamination, foreign_cultures = (
                detect_contamination(
                    retrieved,
                    test["expected_culture"]
                )
            )


            # ------------------------------------------------
            # 4. VERIFICATION SECTION
            # ------------------------------------------------

            expected_section = test.get(
                "expected_section"
            )

            section_found = detect_expected_section(
                retrieved,
                expected_section
            )


            # ------------------------------------------------
            # 5. CONSTRUCTION DU CONTEXTE
            # ------------------------------------------------

            # On conserve ici les deux premiers chunks,
            # comme dans ta version actuelle.

            context = retriever.format_context(
                retrieved[:2]
            )


            # ------------------------------------------------
            # 6. GENERATION
            # ------------------------------------------------

            answer = llm.generate(
                question=question,
                context=context
            )


            elapsed = time.time() - start_time


            # ------------------------------------------------
            # 7. SCORE MOTS-CLES
            # ------------------------------------------------

            keyword_result = calculate_keyword_score(
                answer,
                test["expected_keywords"]
            )


            # ------------------------------------------------
            # 8. DETECTION DE LA CULTURE
            # ------------------------------------------------

            detected_culture = retriever.detect_culture(
                question
            )


            detected_culture_name = (
                detected_culture.get("culture")
                if detected_culture
                else None
            )


            # ------------------------------------------------
            # 9. STATUT
            # ------------------------------------------------

            status = determine_status(
                test=test,
                answer=answer,
                keyword_result=keyword_result,
                contamination=contamination
            )


            # ------------------------------------------------
            # 10. AFFICHAGE
            # ------------------------------------------------

            print("\nCulture détectée :")

            print(
                f"  {detected_culture_name}"
            )


            print("\nCultures récupérées :")

            if culture_counts:

                for culture, count in (
                    culture_counts.items()
                ):

                    print(
                        f"  - {culture} : {count}"
                    )

            else:

                print("  Aucune")


            print("\nSections récupérées :")

            if section_counts:

                for section, count in (
                    section_counts.items()
                ):

                    print(
                        f"  - {section} : {count}"
                    )

            else:

                print("  Aucune")


            print("\nSection attendue :")

            print(
                f"  {expected_section}"
            )


            print("\nSection attendue retrouvée :")

            print(
                "  OUI"
                if section_found
                else "  NON"
            )


            print("\nContamination inter-culture :")

            if contamination:

                print("  OUI")

                print(
                    "  Cultures étrangères :"
                )

                for culture in foreign_cultures:

                    print(
                        f"    - {culture}"
                    )

            else:

                print("  NON")


            # ------------------------------------------------
            # CHUNKS
            # ------------------------------------------------

            print("\nChunks récupérés :")

            for i, chunk in enumerate(
                retrieved,
                start=1
            ):

                metadata = chunk["metadata"]

                print(
                    f"  {i}. "
                    f"{metadata.get('culture')} | "
                    f"{metadata.get('section')} | "
                    f"distance={chunk['distance']}"
                )


            # ------------------------------------------------
            # REPONSE
            # ------------------------------------------------

            print("\nRéponse :")

            print(answer)


            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            if keyword_result:

                print("\nScore mots-clés :")

                print(
                    f"  "
                    f"{keyword_result['score']}%"
                )


                if keyword_result["found"]:

                    print(
                        "  Mots-clés trouvés :"
                    )

                    for keyword in (
                        keyword_result["found"]
                    ):

                        print(
                            f"    + {keyword}"
                        )


                if keyword_result["missing"]:

                    print(
                        "  Mots-clés manquants :"
                    )

                    for keyword in (
                        keyword_result["missing"]
                    ):

                        print(
                            f"    - {keyword}"
                        )

            else:

                print(
                    "\nScore mots-clés : N/A"
                )


            # ------------------------------------------------
            # TEST ABSENCE
            # ------------------------------------------------

            if test.get("expected_absent"):

                absence_message_found = (
                    normalize(ABSENT_MESSAGE)
                    in normalize(answer)
                )

                print(
                    "\nMessage d'absence attendu :"
                )

                print(
                    "  TROUVÉ"
                    if absence_message_found
                    else "  NON TROUVÉ"
                )

            else:

                absence_message_found = None


            # ------------------------------------------------
            # TEMPS
            # ------------------------------------------------

            print(
                f"\nTemps : {elapsed:.2f}s"
            )


            print(
                f"\nSTATUT : {status}"
            )


            # ------------------------------------------------
            # SAUVEGARDE
            # ------------------------------------------------

            results_report.append({

                "id": test["id"],

                "category": test["category"],

                "question": question,

                "expected_culture":
                    test["expected_culture"],

                "expected_section":
                    test["expected_section"],

                "detected_culture":
                    detected_culture_name,

                "retrieved_cultures":
                    list(culture_counts.keys()),

                "retrieved_sections":
                    list(section_counts.keys()),

                "section_found":
                    section_found,

                "contamination":
                    contamination,

                "foreign_cultures":
                    foreign_cultures,

                "expected_absent":
                    test.get(
                        "expected_absent",
                        False
                    ),

                "absence_message_found":
                    absence_message_found,

                "keyword_score":
                    (
                        keyword_result["score"]
                        if keyword_result
                        else None
                    ),

                "found_keywords":
                    (
                        keyword_result["found"]
                        if keyword_result
                        else []
                    ),

                "missing_keywords":
                    (
                        keyword_result["missing"]
                        if keyword_result
                        else []
                    ),

                "status":
                    status,

                "time":
                    round(elapsed, 2),

                "answer":
                    answer
            })


        except Exception as e:

            elapsed = time.time() - start_time

            print(
                "\nERREUR TECHNIQUE :"
            )

            print(e)


            results_report.append({

                "id": test["id"],

                "category": test["category"],

                "question": question,

                "expected_culture":
                    test["expected_culture"],

                "expected_section":
                    test["expected_section"],

                "status": "ERROR",

                "error": str(e),

                "time":
                    round(elapsed, 2)
            })


    # ========================================================
    # RAPPORT FINAL
    # ========================================================

    print("\n\n")

    print("=" * 70)

    print(
        "                    RAPPORT GLOBAL"
    )

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


    # ========================================================
    # STATISTIQUES
    # ========================================================

    print(
        f"\nNombre total de tests : {total}"
    )

    print(
        f"PASS : {passed}"
    )

    print(
        f"REVIEW : {review}"
    )

    print(
        f"FAIL : {failed}"
    )

    print(
        f"ERROR : {errors}"
    )


    if total:

        strict_success_rate = (
            passed / total * 100
        )

        print(
            f"\nTaux de réussite strict : "
            f"{strict_success_rate:.2f}%"
        )


    if scored:

        average_score = (
            sum(scored) / len(scored)
        )

        print(
            f"Score moyen mots-clés : "
            f"{average_score:.2f}%"
        )


    if times:

        average_time = (
            sum(times) / len(times)
        )

        print(
            f"Temps moyen : "
            f"{average_time:.2f}s"
        )


    print(
        f"Tests avec contamination "
        f"inter-culture : {contaminated}"
    )


    # ========================================================
    # TABLEAU FINAL
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

        score = r.get(
            "keyword_score"
        )

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

    print(
        "                  POINTS À ANALYSER"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # Contamination
    # --------------------------------------------------------

    print(
        "\n1. CONTAMINATION INTER-CULTURE"
    )


    contaminated_tests = [
        r
        for r in results_report
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

        print(
            "Aucune contamination détectée."
        )


    # --------------------------------------------------------
    # Tests à revoir
    # --------------------------------------------------------

    print(
        "\n2. TESTS À REVOIR"
    )


    review_tests = [
        r
        for r in results_report
        if r["status"] in [
            "REVIEW",
            "FAIL"
        ]
    ]


    if review_tests:

        for r in review_tests:

            print(
                f"\n{r['id']} — "
                f"{r['question']}"
            )

            print(
                f"Statut : "
                f"{r['status']}"
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

            if r.get("missing_keywords"):

                print(
                    "Mots-clés manquants : "
                    f"{r['missing_keywords']}"
                )

    else:

        print(
            "Aucun test à revoir."
        )


    # ========================================================
    # GENERATION DES RAPPORTS
    # ========================================================

    json_path = save_json_report(
        results_report
    )


    csv_path = save_csv_report(
        results_report
    )


    txt_path = save_text_report(
        results_report=results_report,
        total=total,
        passed=passed,
        review=review,
        failed=failed,
        errors=errors,
        contaminated=contaminated,
        scored=scored,
        times=times
    )


    # ========================================================
    # FIN
    # ========================================================

    print("\n")

    print("=" * 70)

    print(
        "                 RAPPORTS GENERES"
    )

    print("=" * 70)

    print(
        f"\nJSON détaillé : "
        f"{json_path}"
    )

    print(
        f"CSV synthétique : "
        f"{csv_path}"
    )

    print(
        f"Résumé texte : "
        f"{txt_path}"
    )


    print("\n")

    print("=" * 70)

    print(
        "                 FIN DES TESTS"
    )

    print("=" * 70)


# ============================================================
# POINT D'ENTREE
# ============================================================

if __name__ == "__main__":
    main()