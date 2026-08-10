from rag.retriever import Retriever
from rag.llm import LLM


question = "Quels sont les ravageurs du rosier ?"

retriever = Retriever()
llm = LLM()

# 1. Détection de la culture
detected = retriever.detect_culture(question)

culture = detected["culture"] if detected else None

print("=" * 70)
print("QUESTION :", question)
print("CULTURE :", culture)

# 2. Récupération filtrée
results = retriever.retrieve(
    query=question,
    k=5,
    culture=culture
)

print("\nCHUNKS RÉCUPÉRÉS :", len(results))

for i, chunk in enumerate(results, 1):

    metadata = chunk["metadata"]

    print(f"\n--- Chunk {i} ---")
    print("Culture :", metadata.get("culture"))
    print("Section :", metadata.get("section"))
    print("Distance :", chunk["distance"])

# 3. On prend UNIQUEMENT le chunk Ravageurs
ravageurs_chunks = [
    chunk
    for chunk in results
    if chunk["metadata"].get("section") == "Ravageurs"
]

print("\nCHUNKS RAVAGEURS :", len(ravageurs_chunks))

if not ravageurs_chunks:
    print("ERREUR : aucun chunk Ravageurs trouvé.")
    exit()

chunk = ravageurs_chunks[0]

# 4. Afficher exactement ce qui sera envoyé au LLM
context = retriever.format_context([chunk])

print("\n" + "=" * 70)
print("CONTEXTE ENVOYÉ AU LLM")
print("=" * 70)
print(context)

# 5. Génération
answer = llm.generate(
    question=question,
    context=context
)

print("\n" + "=" * 70)
print("RÉPONSE DU LLM")
print("=" * 70)
print(answer)

print("\n" + "=" * 70)