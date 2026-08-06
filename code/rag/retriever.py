from rag.vector_store import VectorStore
from rag.embedder import Embedder


class Retriever:

    def __init__(self):

        self.embedder = Embedder()
        self.vector_store = VectorStore()


    def retrieve(
        self,
        query,
        k=10,
        family=None,
        culture=None,
        section=None,
    ):

        where={}

        if family:
            where["family"] = family

        if culture:
            where["culture"] = culture

        if section:
            where["section"] = section


        if not where:
            where=None


        results = self.vector_store.search(
            query=query,
            embedder=self.embedder,
            k=k,
            where=where
        )


        output=[]


        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            output.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": round(distance,4)
                }
            )
        output = self.rerank_results(query, output)
        return output



    def format_context(self,chunks):

        context=[]

        for chunk in chunks:

            metadata=chunk["metadata"]

            context.append(
                f"[{metadata['family']} > "
                f"{metadata['culture']} > "
                f"{metadata['section']}]\n\n"
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

            # -----------------------
            # Bonus culture
            # -----------------------
            culture = metadata.get("culture", "").lower()

            if culture and culture in query_lower:
                rerank_score += 0.30

            # -----------------------
            # Bonus section
            # -----------------------
            section = metadata.get("section", "").lower()

            if section and section in query_lower:
                rerank_score += 0.20

            # -----------------------
            # Bonus mots communs
            # -----------------------
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