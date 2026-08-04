
from sentence_transformers import SentenceTransformer


class Embedder :
    """
    transforme un texte en vecteur d'embedder
    """
    def __init__(
        self,
        model_name="BAAI/bge-m3"
    ):
        self.model = SentenceTransformer(model_name)

    def embed(self, text):
        """
        Retourne l'embedding d'un texte.
        """

        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()
    
#Pourquoi tolist() ?

#Parce que encode() retourne un numpy.ndarray. 
# ChromaDB accepte les listes Python (list[float]) 
# et c'est également plus simple si tu veux sérialiser les données.