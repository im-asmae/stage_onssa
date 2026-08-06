from pathlib import Path
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir, exists_in
from whoosh import scoring
import re

from whoosh.analysis import StemmingAnalyzer

class KeywordStore:
    """
    Index lexical basé sur Whoosh.
    Permet la recherche par mots-clés (BM25).
    """

    def __init__(
        self,
        index_dir="whoosh_index"
    ):

        self.index_dir = Path(index_dir)

        analyzer = StemmingAnalyzer()

        self.schema = Schema(
            id=ID(stored=True, unique=True),
            family=TEXT(stored=True, analyzer=analyzer),
            culture=TEXT(stored=True, analyzer=analyzer),
            section=TEXT(stored=True, analyzer=analyzer),
            content=TEXT(stored=True, analyzer=analyzer),
        )

        # Création du dossier si nécessaire
        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Création ou ouverture de l'index
        if exists_in(self.index_dir):
            self.index = open_dir(self.index_dir)
        else:
            self.index = create_in(
                self.index_dir,
                self.schema
            )

    def reset(self):
        """
        Supprime complètement l'index puis le recrée.
        """

        import shutil

        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.index = create_in(
            self.index_dir,
            self.schema
        )

    def add_chunks(self, chunks):
        """
        Indexe tous les chunks dans Whoosh.
        """

        writer = self.index.writer()

        for chunk in chunks:

            metadata = chunk.metadata

            writer.add_document(
                id=chunk.id,
                family=metadata.get("family", ""),
                culture=metadata.get("culture", ""),
                section=metadata.get("section", ""),
                content=chunk.text
            )

        writer.commit()

        print(f"{len(chunks)} chunks indexés dans Whoosh.")

    def clean_query(self, query: str) -> str:
        """
        Nettoie la requête avant de l'envoyer à Whoosh.
        """

        query = query.lower()

        # enlever la ponctuation
        query = re.sub(r"[^\w\s]", " ", query)

        # mots très fréquents inutiles
        stopwords = {
            "comment",
            "quel",
            "quelle",
            "quels",
            "quelles",
            "est",
            "sont",
            "les",
            "des",
            "de",
            "du",
            "la",
            "le",
            "un",
            "une",
            "pour",
            "avec",
            "dans",
            "sur",
            "au",
            "aux"
        }

        words = [
            w
            for w in query.split()
            if w not in stopwords and len(w) > 2
        ]

        return " ".join(words)

        
    def search(self, query, k=5):
        """
        Recherche lexicale BM25.
        """

        output = []

        with self.index.searcher(weighting=scoring.BM25F()) as searcher:

            print("Nombre de documents :", searcher.doc_count())
            print("Requête :", query)

            parser = MultifieldParser(
                ["content", "culture", "family", "section"],
                schema=self.index.schema
            )

            query = self.clean_query(query)

            print("Requête nettoyée :", query)

            q = parser.parse(query)

            print("Whoosh query :", q)

            results = searcher.search(
                q,
                limit=k
            )
            print("Whoosh hits :", len(results))

            for hit in results:

                output.append(
                    {
                        "id": hit["id"],
                        "text": hit["content"],
                        "metadata": {
                            "family": hit["family"],
                            "culture": hit["culture"],
                            "section": hit["section"],
                        },
                        "score": round(hit.score, 4)
                    }
                )

        return output