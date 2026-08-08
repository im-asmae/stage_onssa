from ollama import Client


class LLM:
    """
    Interface avec un modèle Ollama local.
    """

    def __init__(
        self,
        model="qwen2.5:7b",
        temperature=0.1
    ):

        self.model = model
        self.temperature = temperature

        # Connexion explicite au serveur Ollama
        self.client = Client(
            host="http://127.0.0.1:11434"
        )


    def generate(self, question, context):
        """
        Génère une réponse à partir du contexte fourni par le Retriever.
        """

        prompt = self.build_prompt(
            question=question,
            context=context
        )


        response = self.client.chat(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": """
Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.

Règles obligatoires :

1. Réponds uniquement à partir du contexte fourni.
2. N'utilise aucune connaissance externe.
3. N'invente jamais une information.
4. Si plusieurs cultures apparaissent, utilise uniquement celle demandée.
5. Si l'information est absente, réponds :

"Cette information n'est pas présente dans le référentiel ONSSA fourni."

6. Ne propose aucun traitement, pesticide ou matière active absent du contexte.
7. Réponds en français avec un style professionnel.
"""
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            options={
                "temperature": self.temperature
            }
        )


        return response["message"]["content"].strip()



    def build_prompt(
        self,
        question,
        context
    ):
        """
        Construction du prompt utilisateur.
        """

        return f"""
            Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.
            Le contexte qui te sera fourni provient du Retriever du système RAG.

            Considère que ce contexte est le plus pertinent disponible.

            Ton rôle est uniquement de reformuler les informations du contexte de manière claire et fidèle.

            N'utilise jamais de connaissances externes et n'invente aucune information.

            ==============================
            CONTEXTE
            ==============================

            {context}

            ==============================
            QUESTION
            ==============================

            {question}

            ==============================
            INSTRUCTIONS
            ==============================

            Le contexte ci-dessus provient directement du référentiel officiel de l'ONSSA.

            Considère que ce contexte a déjà été sélectionné comme étant le plus pertinent pour répondre à la question.

            Ta tâche consiste uniquement à expliquer ou reformuler les informations présentes dans ce contexte.

            Règles :

            - Utilise exclusivement les informations présentes dans le contexte.
            - N'utilise jamais de connaissances externes.
            - N'invente jamais une information absente.
            - Ignore les autres cultures éventuellement présentes dans le contexte et concentre-toi uniquement sur celle correspondant à la question.
            - Si le contexte contient un couple « Usage » / « Cible », considère que cette information est suffisante pour répondre et reformule-la dans une phrase naturelle.
            - Ne recommande jamais un pesticide, une matière active, une dose, un produit commercial ou une méthode qui n'apparaît pas explicitement dans le contexte.
            - Si aucune information du contexte ne correspond réellement à la question, réponds exactement :

            Cette information n'est pas présente dans le référentiel ONSSA fourni.

            La réponse doit être concise (une ou deux phrases) et rédigée en français.
            """