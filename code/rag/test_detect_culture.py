from rag.retriever import Retriever


retriever = Retriever()


questions = [
    "Quels sont les ravageurs du rosier ?",
    "Quels traitements sont prévus sur l'oranger ?",
    "Quels sont les ravageurs du bananier ?",
    "Quels traitements sont prévus pour le fraisier ?",
    "Quels sont les traitements contre les pucerons ?",
    "Quelle est la capitale du Maroc ?",
]


for question in questions:

    culture = retriever.detect_culture(question)

    print(f"\nQuestion : {question}")
    print(f"Culture détectée : {culture}")