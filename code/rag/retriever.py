from rag.vector_store import VectorStore
from rag.embedder import Embedder

import re
import unicodedata

class Retriever:

    def __init__(self):

        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def _normalize_text(self, text):
        """
        Normalise un texte pour faciliter la comparaison :
        - minuscules
        - suppression des accents
        - espaces normalisés
        """
        text = text.lower().strip()

        text = unicodedata.normalize("NFD", text)
        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Mn"
        )

        text = re.sub(r"\s+", " ", text)

        return text

    def detect_culture(self, question):
        """
        Détecte une culture présente dans la base à partir de la question.

        Retourne :
            {
                "status": "FOUND",
                "culture": "Rosier"
            }

        ou :

            {
                "status": "NONE",
                "culture": None
            }
        """

        cultures = self.vector_store.get_cultures()

        question_normalized = self._normalize_text(question)

        matches = []

        for culture in cultures:

            culture_normalized = self._normalize_text(culture)

            pattern = r"\b" + re.escape(culture_normalized) + r"\b"

            if re.search(pattern, question_normalized):
                matches.append(culture)

        if matches:

            # Si plusieurs correspondances existent,
            # on garde la plus longue.
            matches.sort(
                key=lambda x: len(
                    self._normalize_text(x)
                ),
                reverse=True
            )

            return {
                "status": "FOUND",
                "culture": matches[0]
            }

        return {
            "status": "NONE",
            "culture": None
        }





    def detect_target(self, question):
        """
        Détecte une cible présente dans la question.

        Retourne :
            {
                "status": "FOUND",
                "target": "Pucerons"
            }

        ou :

            {
                "status": "NONE",
                "target": None
            }
        """

        results = self.vector_store.collection.get(
            include=["documents"]
        )

        question_normalized = self._normalize_text(question)

        targets = set()

        for document in results["documents"]:

            for line in document.splitlines():

                line = line.strip()

                if line.lower().startswith("cible :"):

                    target = line.split(":", 1)[1].strip()

                    if target:
                        targets.add(target)

        matches = []

        for target in targets:

            target_normalized = self._normalize_text(target)

            if target_normalized in question_normalized:

                matches.append(target)

        if matches:

            matches.sort(
                key=lambda x: len(
                    self._normalize_text(x)
                ),
                reverse=True
            )

            return {
                "status": "FOUND",
                "target": matches[0]
            }

        return {
            "status": "NONE",
            "target": None
        }


    def detect_section(self, question):
        """
        Détecte une section du référentiel présente dans la question.

        Sections principales :
            - Ravageurs
            - Maladies
            - Adventices
            - Divers

        Retourne :
            {
                "status": "FOUND",
                "section": "Ravageurs"
            }

        ou :

            {
                "status": "NONE",
                "section": None
            }
        """

        sections = [
            "Ravageurs",
            "Maladies",
            "Adventices",
            "Divers"
        ]

        question_normalized = self._normalize_text(question)

        matches = []

        for section in sections:

            section_normalized = self._normalize_text(section)

            if section_normalized in question_normalized:

                matches.append(section)

        if matches:

            matches.sort(
                key=lambda x: len(
                    self._normalize_text(x)
                ),
                reverse=True
            )

            return {
                "status": "FOUND",
                "section": matches[0]
            }

        return {
            "status": "NONE",
            "section": None
        }


    
    def retrieve(
        self,
        query,
        k=10,
        family=None,
        culture=None,
        section=None,
    ):
        """
        Recherche des chunks pertinents.

        Détecte automatiquement :
        - la culture
        - la section

        si elles ne sont pas fournies explicitement.
        """

        # ==========================================================
        # 1. DÉTECTION AUTOMATIQUE DE LA CULTURE
        # ==========================================================

        if culture is None:

            detected_culture = self.detect_culture(query)

            if detected_culture["status"] == "FOUND":
                culture = detected_culture["culture"]

        # ==========================================================
        # 2. DÉTECTION AUTOMATIQUE DE LA SECTION
        # ==========================================================

        if section is None:

            detected_section = self.detect_section(query)

            if detected_section["status"] == "FOUND":
                section = detected_section["section"]

        # ==========================================================
        # 3. CONSTRUCTION DES FILTRES
        # ==========================================================

        filters = []

        if family:
            filters.append({
                "family": {
                    "$eq": family
                }
            })

        if culture:
            filters.append({
                "culture": {
                    "$eq": culture
                }
            })

        if section:
            filters.append({
                "section": {
                    "$eq": section
                }
            })

        # ==========================================================
        # 4. CONSTRUCTION DU WHERE CHROMADB
        # ==========================================================

        if len(filters) == 0:

            where = None

        elif len(filters) == 1:

            where = filters[0]

        else:

            where = {
                "$and": filters
            }

        # ==========================================================
        # 5. RECHERCHE VECTORIELLE
        # ==========================================================

        results = self.vector_store.search(
            query=query,
            embedder=self.embedder,
            k=k,
            where=where
        )

        # ==========================================================
        # 6. FORMATAGE
        # ==========================================================

        output = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):

            output.append({
                "text": document,
                "metadata": metadata,
                "distance": round(distance, 4)
            })

        # ==========================================================
        # 7. RERANKING
        # ==========================================================

        output = self.rerank_results(
            query,
            output
        )

        return output


    def retrieve_by_target(self, target):
        """
        Recherche toutes les cultures associées à une cible.
        """

        data = self.vector_store.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        output = []

        target_normalized = self._normalize_text(target)

        for document, metadata in zip(
            data["documents"],
            data["metadatas"]
        ):

            document_normalized = self._normalize_text(document)

            if target_normalized not in document_normalized:
                continue

            # Vérification plus précise :
            # on vérifie que la cible apparaît réellement
            # dans une ligne "Cible :"
            found = False

            for line in document.splitlines():

                line = line.strip()

                if line.lower().startswith("cible :"):

                    value = line.split(":", 1)[1].strip()

                    if self._normalize_text(value) == target_normalized:
                        found = True
                        break

            if found:

                output.append(
                    {
                        "text": document,
                        "metadata": metadata,
                        "distance": 0.0,
                        "rerank_score": 1.0
                    }
                )

        return output






    def format_context(self,chunks):

        context=[]

        for chunk in chunks:

            metadata = chunk["metadata"]

            family = metadata.get("family", "")
            culture = metadata.get("culture", "")
            section = metadata.get("section", "")

            if section == "__NO_SECTION__":
                header = f"[{family} > {culture}]"
            else:
                header = f"[{family} > {culture} > {section}]"

            context.append(
                f"{header}\n\n"
                f"{chunk['text']}"
        )


        return "\n\n==============================\n\n".join(context)



    # reranking léger, sans modèle supplémentaire (CrossEncoder). 
    # On va simplement réordonner les résultats de ChromaDB avec quelques règles métier. 
    # C'est très efficace pour un référentiel comme celui de l'ONSSA.
    def rerank_results(self, query, chunks):
        """
        Réordonne les résultats avec quelques règles métier.
        """

        query_lower = query.lower()

        for chunk in chunks:

            metadata = chunk["metadata"]
            text = chunk["text"].lower()

            # Base : plus la distance est petite, mieux c'est
            rerank_score = 2 - chunk["distance"]

            # Bonus culture
            culture = metadata.get("culture", "").lower()

            if culture and culture in query_lower:
                rerank_score += 0.30

            # Bonus section
            section = metadata.get("section", "").lower()

            if section and section in query_lower:
                rerank_score += 0.20

            # Bonus mots communs
            words = [
                w.strip(" ?!.,;:")
                for w in query_lower.split()
                if len(w) > 3
            ]

            text_words = set(text.split())

            overlap = sum(
                1
                for word in words
                if word in text_words
            )

            rerank_score += overlap * 0.05

            chunk["rerank_score"] = round(rerank_score, 4)

        chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return chunks