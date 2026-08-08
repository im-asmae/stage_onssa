from rag.retriever import Retriever
from rag.llm import LLM


class RAGPipeline:

    def __init__(self):

        self.retriever = Retriever()
        self.llm = LLM()

    def ask(self, question):

        results = self.retriever.retrieve(
            query=question,
            k=5
        )

        context = self.retriever.format_context(
            results[:2]
        )

        answer = self.llm.generate(
            question=question,
            context=context
        )

        return answer, results