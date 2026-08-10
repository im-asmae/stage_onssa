import chromadb
import time


class VectorStore:

    def __init__(self, path="chroma_db", collection_name="onssa"):

        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=path
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
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

    def add_chunks(self, chunks, embedder, batch_size=64):
        """
        Indexation des chunks par lots.
        """

        start = time.time()


        for i in range(0, len(chunks), batch_size):

            batch = chunks[i:i + batch_size]


            texts = [
                chunk.text
                for chunk in batch
            ]


            embeddings = embedder.embed_batch(texts)


            ids = [
                chunk.id
                for chunk in batch
            ]


            documents = texts


            metadatas = []

            for chunk in batch:

                metadata = dict(chunk.metadata)

                metadata["culture"] = chunk.culture

                metadatas.append(metadata)



            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )


            print(
                f"Indexés : {min(i + batch_size, len(chunks))}/{len(chunks)}"
            )


        elapsed = time.time() - start


        print(
            f"\n{len(chunks)} chunks indexés en {elapsed:.2f} secondes."
        )
    def search(self, query, embedder, k=5, where=None):

        query_embedding = embedder.embed(query)

        results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

        return results

    def count(self):
        return self.collection.count()

    def reset(self):

        try:
            self.client.delete_collection(
                self.collection_name
            )

        except Exception:
            pass


        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def get_cultures(self):
        """
        Retourne les cultures uniques présentes dans la collection.
        """
        results = self.collection.get(
            include=["metadatas"]
        )

        cultures = set()

        for metadata in results["metadatas"]:
            culture = metadata.get("culture")

            if culture:
                cultures.add(culture)

        return sorted(cultures)