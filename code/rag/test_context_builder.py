from rag.retriever import Retriever
from rag.context_builder import ContextBuilder

retriever = Retriever()
builder = ContextBuilder()

question = "Comment traiter les pucerons du oranger ?"

results = retriever.retrieve(question)

context = builder.build(results)

print(context)