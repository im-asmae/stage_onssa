from rag.retrieval import Retriever
from rag.context_builder import ContextBuilder
from rag.llm import LLM


class RAGPipeline:

    def __init__(self):

        self.retriever = Retriever()
        self.context_builder = ContextBuilder()
        self.llm = LLM()

    def ask(self, question):

        # 1 Retrieval
        results = self.retriever.retrieve(question)

        # 2 Context
        context = self.context_builder.build(results)

        # 3 Generation
        answer = self.llm.generate(
            question=question,
            context=context
        )

        return answer