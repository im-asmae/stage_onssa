from rag.pipeline import RAGPipeline

rag = RAGPipeline()

question = input("Question : ")

print("\nRecherche en cours...\n")

answer = rag.ask(question)

print("=" * 80)
print(answer)