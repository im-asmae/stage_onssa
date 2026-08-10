# Rapport de test — Agent RAG ONSSA

## 1. Résumé général

| Indicateur | Résultat |
|---|---:|
| Nombre total de tests | 15 |
| Tests réussis | 9 |
| Tests à revoir | 5 |
| Tests échoués | 1 |
| Erreurs techniques | 0 |
| Score moyen des mots-clés | 85.99% |
| Temps moyen par requête | 86.75s |
| Résultats potentiellement hors culture | 45 |

---

## 2. Taux de réussite

**Taux de réussite strict :**
60.0%

---

## 3. Résultats détaillés

| ID | Catégorie | Score | Chunks | Statut |
|---|---|---:|---:|---|
| T01 | Recherche directe | 100.0% | 5 | PASS |
| T02 | Question ciblée | 100.0% | 5 | PASS |
| T03 | Recherche de traitements | 100.0% | 5 | PASS |
| T04 | Changement de culture | 71.43% | 5 | REVIEW |
| T05 | Question ciblée | 100.0% | 5 | PASS |
| T06 | Changement de culture | 75.0% | 5 | REVIEW |
| T07 | Information absente | N/A | 5 | REVIEW |
| T08 | Changement de section | 100.0% | 5 | PASS |
| T09 | Changement de section | 100.0% | 5 | PASS |
| T10 | Changement de section | 100.0% | 5 | PASS |
| T11 | Robustesse | 71.43% | 5 | REVIEW |
| T12 | Paraphrase | 100.0% | 5 | PASS |
| T13 | Relation culture-cible-usage | 100.0% | 5 | PASS |
| T14 | Relation usage-cible | 0.0% | 5 | FAIL |
| T15 | Hors domaine | N/A | 5 | REVIEW |


---

## 4. Tests échoués ou à revoir


### T04 — Quels sont les ravageurs du rosier ?

**Statut :** REVIEW

**Score :** 71.43%

**Mots-clés manquants :**
Nématodes, Insectes

**Réponse :**

Les ravageurs du rosier selon le référentiel ONSSA sont les acariens, les mouches blanches, les noctuelles défoliatrices, les cochenilles et les pucerons.

---


### T06 — Quels ravageurs sont concernés par des traitements sur le bananier ?

**Statut :** REVIEW

**Score :** 75.0%

**Mots-clés manquants :**
Nématodes

**Réponse :**

Les ravageurs concernés par des traitements sur le bananier sont les acariens, les mouches blanches et les noctuelles défoliatrices.

---


### T07 — Quels traitements sont prévus contre les pucerons sur le bananier ?

**Statut :** REVIEW

**Score :** None%

**Mots-clés manquants :**


**Réponse :**

Cette information n'est pas présente dans le référentiel ONSSA fourni.

---


### T11 — Quels sont les ravageurs du fraisier ?

**Statut :** REVIEW

**Score :** 71.43%

**Mots-clés manquants :**
Nématodes, Drosophila suzukii

**Réponse :**

Les ravageurs du fraisier selon le référentiel ONSSA sont les acariens, les mouches blanches, les drosophiles suzukii, les noctuelles défoliatrices, les pucerons et les thrips.

---


### T14 — Quel ravageur de l'oranger est traité au niveau du sol ?

**Statut :** FAIL

**Score :** 0.0%

**Mots-clés manquants :**
Nématodes, Traitement du sol

**Réponse :**

Le ravageur de l'oranger traité au niveau du sol est le nématode.

---


### T15 — Quelle est la capitale du Maroc ?

**Statut :** REVIEW

**Score :** None%

**Mots-clés manquants :**


**Réponse :**

Cette information n'est pas présente dans le référentiel ONSSA fourni.

---


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
