from sentence_transformers import SentenceTransformer

class Embedder:

    def __init__(self, model_name="BAAI/bge-m3"):

        self.model = SentenceTransformer(model_name)


    def embed(self, text):
        """
        Embedding d'un seul texte.
        Utilisé pour les requêtes utilisateur.
        """

        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()


    def embed_batch(self, texts):
        """
        Embedding de plusieurs textes.
        Utilisé lors de l'indexation.
        """

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        ).tolist()