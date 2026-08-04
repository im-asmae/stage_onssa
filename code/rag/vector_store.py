import chromadb
import time


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="onssa"
        )


    def add_chunk(self, chunk, embedding):

        metadata = dict(chunk.metadata)
        metadata["culture"] = chunk.culture

        self.collection.add(

            ids=[chunk.id],

            documents=[chunk.text],

            embeddings=[embedding],

            metadatas=[metadata]

        )

    
    def add_chunks(self, chunks, embedder):

        start = time.time()

        for chunk in chunks:

            embedding = embedder.embed(chunk.text)

            self.add_chunk(chunk, embedding)

        elapsed = time.time() - start

        print(f"{len(chunks)} chunks indexés en {elapsed:.2f} secondes.")

    
    def search(self, query, embedder, k=5, where=None):

        query_embedding = embedder.embed(query)

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where
        )
    
    def count(self):
        return self.collection.count()
    
    def reset(self):
        self.client.delete_collection("onssa")

        self.collection = self.client.get_or_create_collection(
            name="onssa"
        )