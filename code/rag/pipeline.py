from rag.retriever import Retriever
from rag.llm import LLM
class RAGPipeline:

    def __init__(self):

        self.retriever = Retriever()
        self.llm = LLM()

    def ask(self, question):

        # 1. Identifier les filtres
        culture, section = self.detect_filters(question)

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

        # 4. Context
        context = self.retriever.format_context(
            results[:1]
        )

        print("\n" + "=" * 70)
        print("CONTEXTE ENVOYÉ AU LLM")
        print("=" * 70)
        print(context)
        print("=" * 70)
        # 5. LLM
        answer = self.llm.generate(
            question=question,
            context=context
        )

        return answer, results