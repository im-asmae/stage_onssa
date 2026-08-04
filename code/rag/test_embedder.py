from embedder import Embedder

embedder = Embedder()

text = "Le citronnier est sensible aux pucerons."

embedding = embedder.embed(text)

print("Type :", type(embedding))
print("Dimension :", len(embedding))
print("5 premières valeurs :")
print(embedding[:5])
print(type(embedding[0]))

print("---------------------------------------")
t1 = "Clémentinier | Parties aériennes | Pucerons"
t2 = "Blé dur | Parties aériennes | Rouilles"

e1 = embedder.embed(t1)
e2 = embedder.embed(t2)

print(len(e1))
print(len(e2))
print(len(e1) == len(e2))