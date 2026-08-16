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

            if culture_normalized in question_normalized:
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

        Si aucune culture n'est fournie explicitement,
        tente de détecter automatiquement la culture
        à partir de la question.
        """

        # 1. Détection automatique de la culture

        detected_culture = None

        if culture is None:
            detected_culture = self.detect_culture(query)

            if detected_culture:
                culture = detected_culture["culture"]

        # 2. Construction du filtre ChromaDB

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

        # 3. Construction du where ChromaDB

        if len(filters) == 0:

            where = None

        elif len(filters) == 1:

            where = filters[0]

        else:

            where = {
                "$and": filters
            }

        # 4. Recherche vectorielle

        results = self.vector_store.search(
            query=query,
            embedder=self.embedder,
            k=k,
            where=where
        )

        # 5. Formatage des résultats

        output = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):

            output.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": round(distance, 4)
                }
            )

        # 6. Reranking

        output = self.rerank_results(
            query,
            output
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