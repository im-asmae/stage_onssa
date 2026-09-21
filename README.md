# ONSSA – Assistant IA pour l’identification des organismes nuisibles

## 1. Présentation

Ce projet a été réalisé dans le cadre d’un stage au sein de la **Direction des Systèmes d’Information (DSI) du Ministère de l’Agriculture**.

L’objectif est de développer un **assistant intelligent basé sur l’approche RAG (Retrieval-Augmented Generation)** permettant d'interroger en langage naturel le **Référentiel des usages agricoles au Maroc de l’ONSSA**.

L’assistant permet notamment d’obtenir des informations concernant :

- les ravageurs d’une culture ;
- les maladies associées à une culture ;
- les organismes nuisibles ;
- les traitements associés ;
- les usages agricoles mentionnés dans le référentiel.

Le système utilise un modèle de langage local afin de générer les réponses à partir des informations récupérées dans la base documentaire.

---

## 2. Architecture du système

Le fonctionnement général du système est le suivant :

**Question utilisateur → Détection de la culture/section → Recherche dans ChromaDB → Construction du contexte → Qwen 2.5:7B → Réponse**

Les principales composantes sont :

- **Référentiel ONSSA** : document source ;
- **Parser** : extraction et structuration des informations du référentiel ;
- **BGE-M3** : génération des représentations vectorielles ;
- **ChromaDB** : stockage et recherche des informations vectorisées ;
- **RAG** : récupération des informations pertinentes et construction du contexte ;
- **Qwen 2.5:7B** : génération de la réponse ;
- **Flask** : interface Web.

---

## 3. Prérequis

Avant de lancer le projet, les éléments suivants doivent être installés :

### Python

Python 3.12 est recommandé pour cet environnement.

### Ollama

Ollama est nécessaire pour exécuter localement le modèle de langage.

Après installation d'Ollama, télécharger le modèle utilisé par le projet :

```powershell
ollama pull qwen2.5:7b
```

Vérifier que le modèle est disponible :

```powershell
ollama list
```

Le modèle `qwen2.5:7b` doit apparaître dans la liste.

---

## 4. Installation du projet

### 4.1. Cloner le dépôt

Cloner la branche contenant la version stable du projet :

```powershell
git clone -b version-organise-stable <URL_DU_DEPOT>
```

Puis accéder au dossier :

```powershell
cd stage_onssa
```

---

### 4.2. Créer un environnement virtuel

Créer l'environnement virtuel :

```powershell
python -m venv venv
```

L'activer sous Windows PowerShell :

```powershell
.\venv\Scripts\Activate.ps1
```

Si l'environnement est correctement activé, le terminal doit afficher :

```text
(venv)
```

---

### 4.3. Installer les dépendances

Installer les bibliothèques nécessaires :

```powershell
pip install -r requirements.txt
```

---

## 5. Structure du projet

```text
stage_onssa/
│
├── app.py
├── requirements.txt
├── README.md
│
├── chroma_db/
│   ├── chroma.sqlite3
│   └── ...
│
├── parser/
│   ├── chunk_builder.py
│   ├── chunk_exporter.py
│   ├── classifier.py
│   ├── document_filter.py
│   ├── exporter.py
│   ├── extractor.py
│   ├── models.py
│   ├── parser.py
│   ├── pdf_types.py
│   ├── chunks_v2.json
│   ├── referentiel.json
│   └── tests/
│
├── rag/
│   ├── context_builder.py
│   ├── embedder.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── retriever.py
│   ├── vector_store.py
│   └── tests/
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── test_results/
    ├── global_test_details.json
    ├── global_test_summary.csv
    └── global_test_summary.txt
```

### Description des principaux dossiers

#### `parser/`

Contient les composants permettant d'extraire, analyser et structurer le contenu du référentiel ONSSA.

Les données structurées produites sont notamment disponibles dans :

- `referentiel.json`
- `chunks_v2.json`

#### `rag/`

Contient le pipeline RAG :

- génération des embeddings ;
- recherche dans ChromaDB ;
- construction du contexte ;
- interaction avec le modèle de langage ;
- génération de la réponse finale.

#### `chroma_db/`

Contient la base vectorielle ChromaDB déjà construite à partir des données du référentiel.

Cette base est fournie avec le projet afin d'éviter de devoir reconstruire l'index avant le premier lancement.

#### `templates/`

Contient les fichiers HTML de l'interface Web Flask.

#### `static/`

Contient les fichiers statiques de l'interface, notamment la feuille de style CSS.

#### `test_results/`

Contient les résultats des tests fonctionnels réalisés sur le système.

---

## 6. Lancement de l'application

### Étape 1 – Vérifier qu'Ollama fonctionne

Dans un terminal :

```powershell
ollama list
```

Vérifier que :

```text
qwen2.5:7b
```

est disponible.

Si nécessaire :

```powershell
ollama pull qwen2.5:7b
```

---

### Étape 2 – Activer l'environnement virtuel

Depuis la racine du projet :

```powershell
.\venv\Scripts\Activate.ps1
```

---

### Étape 3 – Lancer Flask

```powershell
python app.py
```

L'application démarre sur :

```text
http://127.0.0.1:5000
```

Ouvrir ensuite cette adresse dans un navigateur.

---

## 7. Utilisation

Une fois l'application ouverte dans le navigateur :

1. saisir une question dans le champ prévu ;
2. envoyer la question ;
3. le système identifie les informations pertinentes ;
4. les informations correspondantes sont récupérées depuis ChromaDB ;
5. le contexte récupéré est transmis au modèle Qwen 2.5:7B ;
6. la réponse générée est affichée dans l'interface.

### Exemples de questions

```text
Quels sont les ravageurs de la tomate ?
```

```text
Quelles maladies concernent l'olivier ?
```

```text
Quels organismes nuisibles sont associés aux agrumes ?
```

```text
Quels ravageurs du blé sont concernés par des traitements ?
```

---

## 8. Tests

Le projet contient plusieurs tests unitaires répartis entre les composants du parser et du pipeline RAG.

Les tests couvrent notamment :

- l'extraction du document ;
- la classification des lignes ;
- la structuration des données ;
- la construction des chunks ;
- la génération des embeddings ;
- la recherche dans ChromaDB ;
- la construction du contexte ;
- l'interaction avec le modèle de langage ;
- le pipeline RAG.

Une batterie de tests fonctionnels globale est également disponible dans :

```text
test_global.py
```

Les résultats sont enregistrés dans :

```text
test_results/
```

avec notamment :

```text
global_test_details.json
global_test_summary.csv
global_test_summary.txt
```

---

## 9. Résultats des tests fonctionnels

La campagne de tests fonctionnels réalisée sur 15 scénarios a donné les résultats suivants :

| Indicateur                              | Résultat |
| --------------------------------------- | -------: |
| Nombre de tests                         |       15 |
| Tests réussis                           |       13 |
| Tests à revoir                          |        1 |
| Tests en échec                          |        1 |
| Erreurs techniques                      |        0 |
| Taux de réussite strict                 |  86,67 % |
| Score moyen de couverture des mots-clés |  90,38 % |
| Tests avec contamination inter-culture  |        0 |
| Temps moyen d'exécution                 |  90,46 s |

Ces résultats montrent que le prototype fonctionne correctement dans la majorité des scénarios testés.

Aucune erreur technique n'a été observée et aucune contamination entre les cultures testées n'a été détectée. Les cas nécessitant une amélioration concernent principalement l'exhaustivité de certaines réponses et la récupération précise de certaines relations entre une culture, un organisme nuisible et son usage.

---

## 10. Technologies utilisées

| Technologie | Rôle                                  |
| ----------- | ------------------------------------- |
| Python      | Langage principal                     |
| Flask       | Interface Web                         |
| BGE-M3      | Modèle d'embeddings                   |
| ChromaDB    | Base vectorielle                      |
| Ollama      | Exécution locale du modèle de langage |
| Qwen 2.5:7B | Génération des réponses               |
| PyMuPDF     | Extraction du contenu PDF             |
| RAG         | Architecture de recherche augmentée   |

---

## 11. Points importants pour le déploiement

### Base ChromaDB

Le dossier :

```text
chroma_db/
```

est fourni avec le projet.

Il ne faut donc pas supprimer ce dossier avant le premier lancement.

Il contient l'index vectoriel nécessaire au fonctionnement du système.

### Modèle Qwen

Le modèle Qwen n'est pas inclus dans le dépôt Git.

Il doit être installé séparément avec Ollama :

```powershell
ollama pull qwen2.5:7b
```

### Exécution locale

Le système est conçu pour fonctionner localement et ne nécessite pas de clé API pour le modèle de langage.

---

## 12. Dépannage

### Le modèle Qwen n'est pas trouvé

Exécuter :

```powershell
ollama list
```

Si `qwen2.5:7b` n'apparaît pas :

```powershell
ollama pull qwen2.5:7b
```

---

### Erreur lors de l'importation d'une bibliothèque

Vérifier que l'environnement virtuel est activé :

```powershell
.\venv\Scripts\Activate.ps1
```

Puis réinstaller les dépendances :

```powershell
pip install -r requirements.txt
```

---

### L'application ne démarre pas

Vérifier que la commande est exécutée depuis la racine du projet :

```text
stage_onssa/
```

Puis :

```powershell
python app.py
```

---

## 13. Limites du prototype

Le système constitue un prototype fonctionnel et présente encore certaines limites :

- certaines réponses peuvent ne pas reprendre l'intégralité des informations disponibles dans le référentiel ;
- certaines relations précises entre les organismes nuisibles et les usages peuvent nécessiter une amélioration du processus de récupération ;
- le temps de réponse dépend notamment de l'exécution locale du modèle de langage ;
- l'application utilise actuellement le serveur de développement Flask pour les tests locaux.

---

## 14. Évolution possible

Plusieurs améliorations peuvent être envisagées :

- amélioration du découpage et de la recherche des documents ;
- amélioration de la précision de la récupération ;
- optimisation du temps de réponse ;
- ajout de nouvelles sources documentaires ;
- amélioration de l'interface Web ;
