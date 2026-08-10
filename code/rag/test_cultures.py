from rag.vector_store import VectorStore

vector_store = VectorStore()

cultures = vector_store.get_cultures()

print("Cultures présentes dans la base :")

for culture in cultures:
    print("-", culture)