from rag.vector_store import VectorStore
from rag.embedder import Embedder


class Retriever:
    """
    Recherche les chunks les plus pertinents
    dans ChromaDB.
    """

    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def retrieve(self, query, k=5):

        results = self.vector_store.search(
            query=query,
            embedder=self.embedder,
            k=k
        )

        return results

    def retrieve_by_culture(self, culture, query, k=5):

        return self.vector_store.search(
            query=query,
            embedder=self.embedder,
            k=k,
            where={"culture": culture}
        )


    #Cette fonction sera très utile juste avant d'appeler le LLM.
    #Au lieu d'envoyer directement le résultat brut de Chroma, on construit un contexte lisible.
    
    def format_context(self, results):

        docs = results["documents"][0]

        return "\n\n-----------------\n\n".join(docs)