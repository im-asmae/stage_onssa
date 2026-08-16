from rag.retriever import Retriever
from rag.llm import LLM


class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever()
        self.llm = LLM()

    def detect_filters(self, question):
        """
        Détecte les filtres principaux à partir de la question.

        Pour le moment, la détection de la culture est déléguée
        au Retriever. La section est détectée à partir des mots
        présents dans la question.
        """

        # Détection de la culture
        detected_culture = self.retriever.detect_culture(question)

        if detected_culture["status"] == "FOUND":
            culture = detected_culture["culture"]
        else:
            culture = None

        # Détection de la section
        question_normalized = self.retriever._normalize_text(question)

        section = None

        sections = [
            "Ravageurs",
            "Maladies",
            "Adventices",
            "Divers"
        ]

        for candidate in sections:
            if self.retriever._normalize_text(candidate) in question_normalized:
                section = candidate
                break

        return culture, section

    def ask(self, question):

        # 1. Identifier les filtres
        culture, section = self.detect_filters(question)

        print("\n" + "=" * 70)
        print("FILTRES DÉTECTÉS")
        print("=" * 70)
        print(f"Culture : {culture}")
        print(f"Section : {section}")
        print("=" * 70)

        # 2. Recherche filtrée
        results = self.retriever.retrieve(
            query=question,
            k=5,
            culture=culture,
            section=section
        )

        # 3. Si aucun résultat
        if not results:
            return (
                "Cette information n'est pas présente dans le référentiel ONSSA fourni.",
                []
            )

        # 4. Construction du contexte
        context = self.retriever.format_context(
            results[:1]
        )

        print("\n" + "=" * 70)
        print("CONTEXTE ENVOYÉ AU LLM")
        print("=" * 70)
        print(context)
        print("=" * 70)

        # 5. Génération de la réponse
        answer = self.llm.generate(
            question=question,
            context=context
        )

        return answer, results