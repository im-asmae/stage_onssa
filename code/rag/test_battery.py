# test_battery.py
"""
Batterie de tests pour évaluer le système RAG ONSSA.

Objectifs :
1. Tester la récupération des bons documents/chunks.
2. Vérifier la pertinence des résultats.
3. Vérifier la fidélité de la réponse au contexte récupéré.
4. Tester les risques de confusion entre cultures.
5. Tester les différents types de questions.
6. Détecter les hallucinations.
7. Générer automatiquement des fichiers de résultats.

Sorties :
    results/test_results.json
    results/test_results.csv
    results/test_report.md
"""

import json
import csv
import os
import time
from datetime import datetime

from rag.pipeline import RAGPipeline


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = "results"

JSON_FILE = os.path.join(OUTPUT_DIR, "test_results.json")
CSV_FILE = os.path.join(OUTPUT_DIR, "test_results.csv")
REPORT_FILE = os.path.join(OUTPUT_DIR, "test_report.md")


# ============================================================
# BATTERIE DE TESTS
# ============================================================

TESTS = [

    # --------------------------------------------------------
    # TEST 1 — Recherche directe d'une liste de ravageurs
    # --------------------------------------------------------
    {
        "id": "T01",
        "category": "Recherche directe",
        "question": "Quels sont les ravageurs de l'oranger ?",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Insectes xylophages",
            "Mineuses des feuilles",
            "Pucerons",
            "Pyrale",
            "Teigne des agrumes"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 2 — Traitement d'un ravageur précis
    # --------------------------------------------------------
    {
        "id": "T02",
        "category": "Question ciblée",
        "question": "Quels traitements sont prévus contre les pucerons sur l'oranger ?",
        "expected_keywords": [
            "Pucerons",
            "Parties aériennes"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 3 — Liste des traitements
    # --------------------------------------------------------
    {
        "id": "T03",
        "category": "Recherche de traitements",
        "question": "Quels traitements sont prévus pour les ravageurs de l'oranger ?",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Insectes xylophages",
            "Mineuses des feuilles",
            "Pucerons"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 4 — Autre culture
    # --------------------------------------------------------
    {
        "id": "T04",
        "category": "Changement de culture",
        "question": "Quels sont les ravageurs du rosier ?",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices",
            "Cochenilles",
            "Pucerons",
            "Insectes"
        ],
        "expected_culture": "Rosier",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 5 — Traitement ciblé autre culture
    # --------------------------------------------------------
    {
        "id": "T05",
        "category": "Question ciblée",
        "question": "Quels traitements sont prévus contre les acariens sur le rosier ?",
        "expected_keywords": [
            "Acariens",
            "Parties aériennes"
        ],
        "expected_culture": "Rosier",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 6 — Bananier
    # --------------------------------------------------------
    {
        "id": "T06",
        "category": "Changement de culture",
        "question": "Quels ravageurs sont concernés par des traitements sur le bananier ?",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Noctuelles défoliatrices"
        ],
        "expected_culture": "Bananier",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 7 — Information absente
    # --------------------------------------------------------
    {
        "id": "T07",
        "category": "Information absente",
        "question": "Quels traitements sont prévus contre les pucerons sur le bananier ?",
        "expected_keywords": [],
        "expected_culture": "Bananier",
        "expected_section": "Ravageurs",
        "should_be_absent": True,
    },

    # --------------------------------------------------------
    # TEST 8 — Maladies
    # --------------------------------------------------------
    {
        "id": "T08",
        "category": "Changement de section",
        "question": "Quelles sont les maladies de l'oranger ?",
        "expected_keywords": [
            "Alternariose",
            "Anthracnose",
            "Bactérioses",
            "Chancre du collet",
            "Fumagine",
            "Fusariose",
            "Pourriture brune",
            "Pourriture grise"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Maladies",
    },

    # --------------------------------------------------------
    # TEST 9 — Adventices
    # --------------------------------------------------------
    {
        "id": "T09",
        "category": "Changement de section",
        "question": "Quels traitements sont prévus contre les adventices de l'oranger ?",
        "expected_keywords": [
            "Adventices",
            "Désherbage"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Adventices",
    },

    # --------------------------------------------------------
    # TEST 10 — Divers
    # --------------------------------------------------------
    {
        "id": "T10",
        "category": "Changement de section",
        "question": "Quels sont les usages concernant l'amélioration du rendement de l'oranger ?",
        "expected_keywords": [
            "Amélioration du rendement",
            "Parties aériennes"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Divers",
    },

    # --------------------------------------------------------
    # TEST 11 — Question sur une autre culture
    # --------------------------------------------------------
    {
        "id": "T11",
        "category": "Robustesse",
        "question": "Quels sont les ravageurs du fraisier ?",
        "expected_keywords": [
            "Nématodes",
            "Acariens",
            "Mouches blanches",
            "Drosophila suzukii",
            "Noctuelles défoliatrices",
            "Pucerons",
            "Thrips"
        ],
        "expected_culture": "Fraisier",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 12 — Question avec formulation différente
    # --------------------------------------------------------
    {
        "id": "T12",
        "category": "Paraphrase",
        "question": "Pour l'oranger, quels nuisibles peuvent faire l'objet d'un traitement ?",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Pucerons"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 13 — Question spécifique sur usage
    # --------------------------------------------------------
    {
        "id": "T13",
        "category": "Relation culture-cible-usage",
        "question": "Pour quels ravageurs de l'oranger le traitement concerne-t-il les parties aériennes ?",
        "expected_keywords": [
            "Acariens",
            "Mouches blanches",
            "Cératite",
            "Cochenilles",
            "Insectes xylophages",
            "Mineuses des feuilles",
            "Pucerons"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 14 — Traitement du sol
    # --------------------------------------------------------
    {
        "id": "T14",
        "category": "Relation usage-cible",
        "question": "Quel ravageur de l'oranger est traité au niveau du sol ?",
        "expected_keywords": [
            "Nématodes",
            "Traitement du sol"
        ],
        "expected_culture": "Oranger",
        "expected_section": "Ravageurs",
    },

    # --------------------------------------------------------
    # TEST 15 — Question hors référentiel
    # --------------------------------------------------------
    {
        "id": "T15",
        "category": "Hors domaine",
        "question": "Quelle est la capitale du Maroc ?",
        "expected_keywords": [],
        "should_be_absent": True,
    },

]


# ============================================================
# OUTILS
# ============================================================

def normalize(text):
    """Normalise un texte pour faciliter les recherches."""
    if text is None:
        return ""

    return (
        text.lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("ë", "e")
        .replace("à", "a")
        .replace("â", "a")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("ô", "o")
        .replace("ù", "u")
        .replace("û", "u")
        .replace("ç", "c")
    )


def keyword_score(answer, expected_keywords):
    """
    Calcule le pourcentage de mots-clés attendus
    présents dans la réponse.
    """

    if not expected_keywords:
        return None, []

    answer_normalized = normalize(answer)

    found = []
    missing = []

    for keyword in expected_keywords:

        if normalize(keyword) in answer_normalized:
            found.append(keyword)
        else:
            missing.append(keyword)

    score = len(found) / len(expected_keywords) * 100

    return round(score, 2), missing


def detect_wrong_cultures(results, expected_culture):
    """
    Détecte grossièrement si les résultats récupérés
    semblent appartenir à d'autres cultures.
    """

    wrong = []

    for result in results:

        text = str(result)

        if expected_culture.lower() not in text.lower():

            # On conserve uniquement les résultats
            # qui semblent explicitement référencer une autre culture.
            if "FAMILLE :" in text and "CULTURE :" in text:
                wrong.append(text[:250])

    return wrong


# ============================================================
# EXECUTION D'UN TEST
# ============================================================

def run_test(pipeline, test):

    print("\n" + "=" * 80)
    print(f"{test['id']} | {test['category']}")
    print("=" * 80)

    print(f"\nQUESTION : {test['question']}")

    start_time = time.time()

    try:

        answer, results = pipeline.ask(test["question"])

        execution_time = round(time.time() - start_time, 2)

        if answer is None:
            answer = ""

        # ----------------------------------------------------
        # Évaluation des mots-clés
        # ----------------------------------------------------

        score, missing_keywords = keyword_score(
            answer,
            test.get("expected_keywords", [])
        )

        # ----------------------------------------------------
        # Détection des cultures incorrectes
        # ----------------------------------------------------

        wrong_cultures = detect_wrong_cultures(
            results,
            test.get("expected_culture", "")
        )

        # ----------------------------------------------------
        # Cas d'information absente
        # ----------------------------------------------------

        answer_normalized = normalize(answer)

        absence_detected = (
            "pas présente" in answer_normalized
            or "pas disponible" in answer_normalized
            or "aucune information" in answer_normalized
            or "information absente" in answer_normalized
            or "ne contient pas" in answer_normalized
        )

        if test.get("should_be_absent"):

            if absence_detected:
                status = "PASS"
            else:
                status = "REVIEW"

        else:

            if score is not None and score >= 80:
                status = "PASS"

            elif score is not None and score >= 50:
                status = "REVIEW"

            else:
                status = "FAIL"

        # ----------------------------------------------------
        # Affichage
        # ----------------------------------------------------

        print("\nRÉPONSE :")
        print(answer)

        print("\n----------------------------------------")
        print("ÉVALUATION")
        print("----------------------------------------")

        print(f"Score mots-clés : {score}%"
              if score is not None
              else "Score mots-clés : N/A")

        print(f"Mots-clés manquants : {missing_keywords}")

        print(f"Nombre de résultats récupérés : {len(results)}")

        print(f"Temps d'exécution : {execution_time}s")

        print(f"Statut : {status}")

        if wrong_cultures:
            print("\n⚠️ Résultats provenant potentiellement d'autres cultures :")
            for item in wrong_cultures[:5]:
                print("-", item)

        return {
            "id": test["id"],
            "category": test["category"],
            "question": test["question"],
            "expected_culture": test.get("expected_culture", ""),
            "expected_section": test.get("expected_section", ""),
            "answer": answer,
            "keyword_score": score,
            "missing_keywords": missing_keywords,
            "retrieved_chunks": len(results),
            "wrong_culture_results": len(wrong_cultures),
            "absence_expected": test.get("should_be_absent", False),
            "absence_detected": absence_detected,
            "status": status,
            "execution_time": execution_time,
            "retrieved_results": results,
        }

    except Exception as e:

        print("\n❌ ERREUR :")
        print(str(e))

        return {
            "id": test["id"],
            "category": test["category"],
            "question": test["question"],
            "expected_culture": test.get("expected_culture", ""),
            "expected_section": test.get("expected_section", ""),
            "answer": "",
            "keyword_score": 0,
            "missing_keywords": [],
            "retrieved_chunks": 0,
            "wrong_culture_results": 0,
            "absence_expected": test.get("should_be_absent", False),
            "absence_detected": False,
            "status": "ERROR",
            "execution_time": 0,
            "retrieved_results": [],
            "error": str(e),
        }


# ============================================================
# GÉNÉRATION DU RAPPORT
# ============================================================

def generate_report(results):

    total = len(results)

    passed = sum(
        1 for r in results
        if r["status"] == "PASS"
    )

    review = sum(
        1 for r in results
        if r["status"] == "REVIEW"
    )

    failed = sum(
        1 for r in results
        if r["status"] == "FAIL"
    )

    errors = sum(
        1 for r in results
        if r["status"] == "ERROR"
    )

    valid_scores = [
        r["keyword_score"]
        for r in results
        if r["keyword_score"] is not None
    ]

    average_score = (
        round(sum(valid_scores) / len(valid_scores), 2)
        if valid_scores
        else 0
    )

    avg_time = (
        round(
            sum(r["execution_time"] for r in results) / total,
            2
        )
        if total
        else 0
    )

    wrong_culture_total = sum(
        r["wrong_culture_results"]
        for r in results
    )

    report = f"""# Rapport de test — Agent RAG ONSSA

## 1. Résumé général

| Indicateur | Résultat |
|---|---:|
| Nombre total de tests | {total} |
| Tests réussis | {passed} |
| Tests à revoir | {review} |
| Tests échoués | {failed} |
| Erreurs techniques | {errors} |
| Score moyen des mots-clés | {average_score}% |
| Temps moyen par requête | {avg_time}s |
| Résultats potentiellement hors culture | {wrong_culture_total} |

---

## 2. Taux de réussite

**Taux de réussite strict :**
{round(passed / total * 100, 2) if total else 0}%

---

## 3. Résultats détaillés

| ID | Catégorie | Score | Chunks | Statut |
|---|---|---:|---:|---|
"""

    for r in results:

        score = (
            f"{r['keyword_score']}%"
            if r["keyword_score"] is not None
            else "N/A"
        )

        report += (
            f"| {r['id']} | {r['category']} | "
            f"{score} | {r['retrieved_chunks']} | "
            f"{r['status']} |\n"
        )

    report += """

---

## 4. Tests échoués ou à revoir

"""

    problematic = [
        r for r in results
        if r["status"] in ["FAIL", "REVIEW", "ERROR"]
    ]

    if not problematic:

        report += "Aucun test problématique détecté automatiquement.\\n"

    else:

        for r in problematic:

            report += f"""
### {r['id']} — {r['question']}

**Statut :** {r['status']}

**Score :** {r['keyword_score']}%

**Mots-clés manquants :**
{", ".join(r['missing_keywords'])}

**Réponse :**

{r['answer']}

---

"""

    report += """
## 5. Ce qu'il faut analyser

### A. Pertinence de la récupération

Vérifier si les chunks récupérés correspondent réellement à :

- la bonne culture ;
- la bonne section ;
- la bonne cible ;
- le bon type d'usage.

Un système RAG peut générer une réponse correcte tout en récupérant trop de contenu inutile.

### B. Précision de la réponse

Vérifier que la réponse :

- reprend uniquement les informations présentes dans le référentiel ;
- ne rajoute pas d'informations externes ;
- ne transforme pas une information partielle en affirmation générale ;
- conserve les noms exacts des ravageurs, maladies et usages.

### C. Hallucinations

Une hallucination correspond ici à une information affirmée par le modèle alors qu'elle n'est pas présente dans le contexte récupéré.

Exemple problématique :

> Le bananier est traité contre les pucerons.

si le contexte récupéré ne contient pas les pucerons pour le bananier.

### D. Confusion entre cultures

C'est actuellement un point particulièrement important.

Exemple :

Question :

> Quels sont les ravageurs du bananier ?

Mais les résultats contiennent :

> CULTURE : Oranger

Cela indique un problème de récupération.

### E. Gestion des informations absentes

Pour une question comme :

> Quels traitements sont prévus contre les pucerons sur le bananier ?

si le référentiel ne contient pas cette information, le système doit le dire clairement.

Il ne doit pas récupérer les pucerons de l'oranger et les attribuer au bananier.

### F. Robustesse aux reformulations

Deux questions différentes mais ayant le même sens devraient idéalement produire des résultats similaires.

Exemple :

> Quels sont les ravageurs de l'oranger ?

et :

> Quels nuisibles peuvent être traités sur l'oranger ?

### G. Pertinence des chunks

Le nombre de chunks n'est pas automatiquement synonyme de qualité.

Un bon résultat est :

> peu de chunks mais très pertinents

plutôt que :

> beaucoup de chunks provenant de cultures différentes.

---

## 6. Interprétation des statuts

### PASS

Le système répond correctement et récupère les informations attendues.

### REVIEW

La réponse contient une partie des informations attendues mais nécessite une vérification humaine.

### FAIL

La réponse est incorrecte, fortement incomplète ou hors contexte.

### ERROR

Une erreur technique empêche l'exécution du test.

---

## 7. Conclusion

Cette batterie de tests permet d'évaluer séparément plusieurs dimensions du système :

1. qualité de la récupération ;
2. pertinence des chunks ;
3. précision de la réponse ;
4. gestion des informations absentes ;
5. résistance aux confusions entre cultures ;
6. résistance aux reformulations ;
7. présence éventuelle d'hallucinations ;
8. temps d'exécution.

Les résultats détaillés doivent être analysés manuellement avant de conclure sur la fiabilité globale du système.
"""

    return report


# ============================================================
# SAUVEGARDE JSON
# ============================================================

def save_json(results):

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=4,
            default=str
        )


# ============================================================
# SAUVEGARDE CSV
# ============================================================

def save_csv(results):

    fields = [
        "id",
        "category",
        "question",
        "expected_culture",
        "expected_section",
        "keyword_score",
        "missing_keywords",
        "retrieved_chunks",
        "wrong_culture_results",
        "absence_expected",
        "absence_detected",
        "status",
        "execution_time",
    ]

    with open(
        CSV_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()

        for result in results:

            row = {
                key: result.get(key, "")
                for key in fields
            }

            row["missing_keywords"] = ", ".join(
                result.get("missing_keywords", [])
            )

            writer.writerow(row)


# ============================================================
# MAIN
# ============================================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("\n")
    print("=" * 80)
    print("       BATTERIE DE TESTS — AGENT RAG ONSSA")
    print("=" * 80)

    print(f"\nNombre de tests : {len(TESTS)}")
    print(f"Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nInitialisation du pipeline...")

    try:

        pipeline = RAGPipeline()

    except Exception as e:

        print("\n❌ Impossible d'initialiser le pipeline.")
        print(e)

        return

    results = []

    for test in TESTS:

        result = run_test(
            pipeline,
            test
        )

        results.append(result)

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    save_json(results)
    save_csv(results)

    report = generate_report(results)

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    # --------------------------------------------------------
    # Résumé final
    # --------------------------------------------------------

    total = len(results)

    passed = sum(
        1 for r in results
        if r["status"] == "PASS"
    )

    review = sum(
        1 for r in results
        if r["status"] == "REVIEW"
    )

    failed = sum(
        1 for r in results
        if r["status"] == "FAIL"
    )

    errors = sum(
        1 for r in results
        if r["status"] == "ERROR"
    )

    print("\n")
    print("=" * 80)
    print("                    RÉSUMÉ FINAL")
    print("=" * 80)

    print(f"\nTests totaux       : {total}")
    print(f"PASS               : {passed}")
    print(f"À revoir           : {review}")
    print(f"FAIL               : {failed}")
    print(f"ERREUR             : {errors}")

    if total:

        print(
            f"\nTaux de réussite   : "
            f"{round(passed / total * 100, 2)}%"
        )

    print("\nFichiers générés :")

    print(f"  → {JSON_FILE}")
    print(f"  → {CSV_FILE}")
    print(f"  → {REPORT_FILE}")

    print("\nFin des tests.")
    print("=" * 80)


if __name__ == "__main__":
    main()