import ollama


class LLM:
    """
    Interface avec le modèle local Ollama.
    """

    def __init__(self, model="qwen2.5:7b"):
        self.model = model

    def generate(self, question, context):
        """
        Génère une réponse à partir du contexte récupéré.
        """

        prompt = self.build_prompt(
            question=question,
            context=context
        )

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content":
                    (
                        "Tu es un expert du référentiel des usages agricoles de l'ONSSA.\n"
                        "Réponds exclusivement à partir du contexte fourni.\n"
                        "N'invente jamais une information absente.\n"
                        "Lorsque le contexte contient plusieurs cultures, concentre-toi uniquement sur celle correspondant à la question.\n"
                        "Si le référentiel ne contient pas la réponse exacte, indique-le clairement."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    def build_prompt(self, question, context):
        """
        Construit le prompt envoyé au LLM.
        """

        return f"""
Contexte :

{context}

----------------------------

Question :

{question}

Réponds uniquement en utilisant les informations du contexte.
"""